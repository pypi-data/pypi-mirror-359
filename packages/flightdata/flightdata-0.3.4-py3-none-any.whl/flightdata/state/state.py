from __future__ import annotations

from pathlib import Path
from typing import Literal, ClassVar, overload

import numpy as np
import numpy.typing as npt
import pandas as pd

import geometry as g
from flightdata import Constructs, Environment, Flight, Flow, Origin, SVar, Table
from schemas import fcj
from flightdata.base.table.slicer import Slicer
from flightdata.state.kinematics import interpolate
from dataclasses import dataclass


@dataclass(repr=False)
class State(Table):
    constructs: ClassVar[Constructs] = Table.constructs + Constructs(
        [
            SVar("pos", g.Point, ["x", "y", "z"], lambda self: g.P0(len(self))),
            SVar(
                "att",
                g.Quaternion,
                ["rw", "rx", "ry", "rz"],
                lambda self: g.Q0(len(self)),
            ),
            SVar(
                "vel",
                g.Point,
                ["u", "v", "w"],
                lambda st: g.P0()
                if len(st) == 1
                else st.att.inverse().transform_point(st.pos.diff(st.dt)),
            ),
            SVar(
                "rvel",
                g.Point,
                ["p", "q", "r"],
                lambda st: g.P0() if len(st) == 1 else st.att.body_diff(st.dt),
            ),
            SVar(
                "acc",
                g.Point,
                ["du", "dv", "dw"],
                lambda st: g.P0()
                if len(st) == 1
                else st.att.inverse().transform_point(
                    st.att.transform_point(st.vel).diff(st.dt) + g.PZ(9.81, len(st))
                ),
            ),
        ]
    )
    _construct_freq: ClassVar[float] = 25

    @overload
    def __getattr__(self, name: Literal["pos"]) -> g.Point: ...
    @overload
    def __getattr__(self, name: Literal["att"]) -> g.Quaternion: ...
    @overload
    def __getattr__(self, name: Literal["vel"]) -> g.Point: ...
    @overload
    def __getattr__(self, name: Literal["rvel"]) -> g.Point: ...
    @overload
    def __getattr__(self, name: Literal["acc"]) -> g.Point: ...
    @overload
    def __getattr__(
        self, name: Literal["x,y,z,rw,rx,ry,rz,u,v,w,du,dv,dw"]
    ) -> npt.NDArray: ...
    @overload
    def __getattr__(self, name: str) -> Slicer: ...

    def __getattr__(self, key):
        return super().__getattr__(key)

    @property
    def transform(self):
        return g.Transformation.build(self.pos, self.att)

    @property
    def back_transform(self):
        return g.Transformation(-self.pos, self.att.inverse())

    @staticmethod
    def from_transform(transform: g.Transformation = None, **kwargs) -> State:
        if transform is None:
            transform = g.Transformation()
        if "time" not in kwargs:
            kwargs["time"] = g.Time.from_t(
                np.linspace(0, State._construct_freq * len(transform), len(transform))
            )
        return State.from_constructs(pos=transform.p, att=transform.q, **kwargs)

    def body_to_world(self, pin: g.Point, rotation_only=False) -> g.Point:
        """Rotate a g.Point in the body frame to a g.Point in the data frame

        Args:
            pin (g.Point): g.Point on the aircraft

        Returns:
            g.Point: g.Point in the world
        """
        if rotation_only:
            return self.transform.rotate(pin)
        else:
            return self.transform.point(pin)

    def world_to_body(self, pin: g.Point, rotation_only=False) -> g.Point:
        if rotation_only:
            self.back_transform.rotate(pin)
        else:
            return self.back_transform.point(pin)

    @property
    def wvel(self) -> g.Point:
        return self.att.transform_point(self.vel)

    @property
    def wacc(self) -> g.Point:
        return self.att.transform_point(self.acc)

    @property
    def wrvel(self) -> g.Point:
        return self.att.transform_point(self.rvel)

    def fill(self, time: g.Time) -> State:
        """Project forward through time assuming uniform circular motion"""
        st = self[-1]
        t = time.t - time.t[0]

        vel: g.Point = st.vel.tile(len(time))
        rvel = (
            g.point.vector_rejection(self.rvel, self.vel).tile(len(time))
            if self.vel != 0
            else self.rvel.tile(len(time))
        )
        att: g.Quaternion = st.att.body_rotate(rvel * t)
        wvel = att.transform_point(self.vel)
        wrvel = att.transform_point(rvel)

        if self.rvel != 0 and self.vel != 0:
            theta = wrvel * t

            r0 = (
                g.point.cross(wrvel[0], wvel[0]).unit()
                * abs(wvel[0])[0]
                / abs(g.point.vector_rejection(wrvel[0], wvel[0]))[0]
            )

            center = self.pos + r0
            radius = g.Quaternion.from_axis_angle(theta).transform_point(-r0)
            acc = -radius.unit() * abs(wvel[0]) ** 2 / abs(radius) + g.PZ(
                9.81, len(time)
            )
            pos = center + radius
        else:
            pos = self.pos + wvel[0] * t
            acc = g.PZ(9.81, len(time))

        return State.from_constructs(
            time, pos, att, vel, rvel, att.inverse().transform_point(acc)
        )

    def plot(self, **kwargs):
        from plotting import plotsec

        return plotsec(self, **(dict(nmodels=10, ribb=True) | kwargs))

    def plotlabels(self, label: str, **kwargs):
        from plotting import plot_regions

        return plot_regions(self, label, **kwargs)

    def extrapolate(self, duration: float, min_len=3) -> State:
        """Extrapolate the input state assuming uniform circular motion and small angles"""
        npoints = np.max([int(np.ceil(duration / self.dt[0])), min_len])
        time = g.Time.from_t(np.linspace(0, duration, npoints))
        return self.fill(time)

    @classmethod
    def from_dict(Cls, data: list[dict[str, float | str]] | dict[str, dict]) -> State:
        if isinstance(data, list):
            # need to reorder the label columns to make sure the labels are nested correctly
            df = pd.DataFrame.from_dict(data).set_index("t", drop=False)
            if "manoeuvre" in df.columns and "element" in df.columns:
                iman = df.columns.get_loc("manoeuvre")
                iel = df.columns.get_loc("element")
                if iman != -1 and iel != -1:
                    cols = df.columns.to_list()
                    cols[min(iman, iel)] = "manoeuvre"
                    cols[max(iman, iel)] = "element"
                    df = df.reindex(cols, axis=1)
                    data = df.to_dict("records")
        return super().from_dict(data)

    @staticmethod
    def from_csv(filename) -> State:
        df = pd.read_csv(filename)

        if (
            "time_index" in df.columns
        ):  # This is for back compatability with old csv files where time column was labelled differently
            if "t" in df.columns:
                df.drop("time_index", axis=1)
            else:
                df = df.rename({"time_index": "t"}, axis=1)
        return State(df.set_index("t", drop=False))

    @staticmethod
    def from_flight(flight: Flight, origin: Origin | str | None = None) -> State:
        if isinstance(origin, str):
            extension = Path(origin).split()[1]
            if extension == "f3a":
                origin = Origin.from_f3a_zone(origin)
            elif extension == "json":
                origin = Origin.from_json(origin)
        elif origin is None:
            origin = flight.origin

        if flight.primary_pos_source.startswith("pos"):
            pos = origin.rotation.transform_point(
                g.GPS(flight.pos.ffill().bfill()) - origin.pos
            )
        else:
            pos = origin.rotation.transform_point(
                g.Point(flight.position.ffill().bfill())
            )

        att = origin.rotation * g.Euler(flight.attitude.ffill().bfill())

        return State.from_constructs(
            g.Time.from_t(np.array(flight.data.time_flight)),
            pos,
            att,
            (
                att.inverse().transform_point(
                    origin.rotation.transform_point(
                        g.Point(flight.velocity.ffill().bfill())
                    )
                )
                if all(flight.contains("velocity"))
                else None
            ),
            (
                g.Point(flight.axisrate.ffill().bfill())
                if all(flight.contains("axisrate"))
                else None
            ),
            (
                g.Point(flight.acceleration.ffill().bfill())
                if all(flight.contains("acceleration"))
                else None
            ),
        )


    @staticmethod
    def kinematic_interpolation(a: State, b: State):
        def interp(fac: float):
            t = a.t[0] + fac * (b.t[0] - a.t[0])
            pos, vel, acc = interpolate(
                a.t[0],
                b.t[0],
                a.pos[0],
                b.pos[0],
                a.att.transform_point(a.vel)[0],
                b.att.transform_point(b.vel)[0],
            )(t)
            att = g.Quaternion.slerp(a.att[0], b.att[0])(fac)
            rvel = g.Point.linterp(a.rvel[0], b.rvel[0])(fac)

            return State.from_constructs(
                g.Time(t, b.t[0] - t),
                pos,
                att,
                att.inverse().transform_point(vel),
                rvel,
                att.inverse().transform_point(acc),
            )

        return interp

    def interpolate_kinematic(self: State, t: float) -> State:
        i0 = self.data.index.get_indexer([t], method="ffill")[0]
        i1 = self.data.index.get_indexer([t], method="bfill")[0]
        if i0 == i1:
            return self.iloc[i0]
        return State.kinematic_interpolation(self.iloc[i0], self.iloc[i1])(
            (t - self.t[i0]) / (self.t[i1] - self.t[i0])
        )

    def splitter_labels(
        self: State,
        mans: list[fcj.Man],
        better_names: list[str] = None,
        target_col="manoeuvre",
        t0=0,
    ) -> State:
        """label the manoeuvres in a State based on the flight coach splitter information

        TODO this assumes the state only contains the dataset contained in the json

        Args:
            mans (list): the mans field of a flight coach json
            better_names: names to replace the splitter names with. does not include takeoff or landing.

        Returns:
            State: State with labelled manoeuvres
        """
        i0 = self.data.index.get_indexer([t0], "nearest")[0]

        takeoff = self.data.iloc[0 : int(mans[0].stop) + i0 + 1]

        labels = [mans[0].name]
        labelled = [State(takeoff).label(**{target_col: labels[0]})]
        if better_names:
            better_names.append("land")

        for i, split_man in enumerate(mans[1:]):
            while split_man.name in labels:
                split_man.name = split_man.name + "2"

            name = better_names[i] if better_names else split_man.name

            labelled.append(
                State(
                    self.data.iloc[
                        int(split_man.start) + i0 : int(split_man.stop) + i0 + 1
                    ]
                ).label(**{target_col: name})
            )
            labels.append(split_man.name)

        return State.stack(labelled)

    def body_rotate(self: State, r: g.Point) -> State:
        """Rotate body axis by an axis angle"""
        att = self.att.body_rotate(r)
        q = att.inverse() * self.att
        return State.from_constructs(
            time=self.time,
            pos=self.pos,
            att=att,
            vel=q.transform_point(self.vel),
            rvel=q.transform_point(self.rvel),
            acc=q.transform_point(self.acc),
        ).label(**self.labels)

    def scale(self: State, factor: float) -> State:
        return State.from_constructs(
            time=self.time,
            pos=self.pos * factor,
            att=self.att,
            vel=self.vel * factor,
            rvel=self.rvel,
            acc=self.acc * factor,
        ).label(**self.labels)

    def mirror_zy(self: State) -> State:
        att = g.Quaternion.from_euler(
            (self.att.to_euler() + g.Point(0, 0, np.pi)) * g.Point(-1, 1, -1)
        )
        return State.from_constructs(
            time=self.time,
            pos=self.pos * g.Point(-1, 1, 1),
            att=att,  # g.Quaternion(self.att.w, self.att.x, -self.att.y, -self.att.z),
            vel=self.vel,
        ).label(**self.labels)

    def to_track(self: State) -> State:
        """This rotates the body so the x axis is in the velocity vector"""
        return self.body_to_wind()

    def body_to_stability(self: State, flow: Flow = None) -> State:
        if not flow:
            env = Environment.from_constructs(self.time)
            flow = Flow.from_body(self, env)
        return self.body_rotate(-g.Point(0, 1, 0) * flow.alpha)

    def stability_to_wind(self: State, flow: Flow = None) -> State:
        if not flow:
            env = Environment.from_constructs(self.time)
            flow = Flow.from_body(self, env)
        return self.body_rotate(g.Point(0, 0, 1) * flow.beta)

    def body_to_wind(self: State, flow: Flow = None) -> State:
        return self.body_to_stability(flow).stability_to_wind(flow)

    def track_to_wind(self: State, env: Environment) -> State:
        """I think the correct way to go from track axis to wind axis is to do a yaw rotation then a pitch
        rotation, as this keeps the wing vector in the track axis XY plane.

        Args:
            self (State): the track axis data
            env (Environment): the environment

        Returns:
            State: the wind axis data
        """
        # the local wind vector in the track frame:
        jwind = self.att.inverse().transform_point(env.wind)

        # the yaw rotation required to align the xz plane with the local wind vector:
        yaw_rotation = (jwind + self.vel).angles(g.PX()) * g.Point(0, 0, 1)

        # transform the data by this yaw rotation:
        int_axis = self.body_rotate(yaw_rotation)

        # the local wind vector in the intermediate frame:
        intwind = int_axis.att.inverse().transform_point(env.wind)

        # the pitch rotation required to align the xy plane with the local wind vector:
        pitch_rotation = (intwind + int_axis.vel).angles(g.PX()) * g.Point(0, 1, 0)

        # transform by this pitch rotation to get the wind axis state
        return int_axis.body_rotate(pitch_rotation)

    def wind_to_body(self: State, flow: Flow) -> State:
        stability_axis = self.body_rotate(-g.Point(0, 0, 1) * flow.beta)
        body_axis = stability_axis.body_rotate(g.Point(0, 1, 0) * flow.alpha)

        return body_axis

    def _create_json_data(self: State) -> pd.DataFrame:
        wvels = self.transform.rotate(self.vel)

        transform = g.Transformation.from_coords(
            g.Coord.from_xy(g.Point(0, 0, 0), g.Point(1, 0, 0), g.Point(0, 1, 0)),
            g.Coord.from_xy(g.Point(0, 0, 0), g.Point(1, 0, 0), g.Point(0, -1, 0)),
        )
        eul = transform.rotate(self.att).to_euler()

        fcd = pd.DataFrame(
            data=dict(
                time=self.t * 1e6,
                N=self.x,
                E=-self.y,
                D=-self.z,
                VN=wvels.x,
                VE=-wvels.y,
                VD=-wvels.z,
                r=np.degrees(eul.x),
                p=np.degrees(eul.y),
                yw=np.degrees(eul.z),
                wN=np.zeros(len(self)),
                wE=np.zeros(len(self)),
                roll=eul.x,
                pitch=eul.y,
                yaw=eul.z,
            ),
        )

        return fcd

    def _create_json_mans(self: State, kfactors: list[int]) -> pd.DataFrame:
        mans = pd.DataFrame(
            columns=[
                "name",
                "id",
                "sp",
                "wd",
                "start",
                "stop",
                "sel",
                "background",
                "k",
            ]
        )
        mnames = self.data.manoeuvre.unique()
        mans["name"] = mnames
        mans["k"] = kfactors
        mans["id"] = ["sp_{}".format(i) for i in range(len(mnames))]

        mans["sp"] = list(range(len(mnames)))

        itsecs = [self.get_manoeuvre(mn) for mn in mnames]

        mans["wd"] = [100 * st.duration / self.duration for st in itsecs]

        dat = self.data.reset_index(drop=True)

        mans["start"] = [dat.loc[dat.manoeuvre == mn].index[0] for mn in mnames]

        mans["stop"] = [dat.loc[dat.manoeuvre == mn].index[-1] + 1 for mn in mnames]

        mans["sel"] = np.full(len(mnames.data), False)
        mans.loc[1, "sel"] = True
        mans["background"] = np.full(len(mnames), "")

        return mans

    def create_fc_json(
        self: State,
        kfactors: list[int],
        schedule_name: str,
        schedule_category: str = "F3A",
    ):
        fcdata = self._create_json_data()
        fcmans = self._create_json_mans(kfactors)
        return {
            "version": "1.3",
            "comments": "DO NOT EDIT\n",
            "name": schedule_name,
            "view": {
                "position": {
                    "x": -120,
                    "y": 130.50000000000003,
                    "z": 264.99999999999983,
                },
                "target": {"x": -22, "y": 160, "z": -204},
            },
            "parameters": {
                "rotation": -1.5707963267948966,
                "start": int(fcmans.iloc[1].start),
                "stop": int(fcmans.iloc[1].stop),
                "moveEast": 0.0,
                "moveNorth": 0.0,
                "wingspan": 3,
                "modelwingspan": 25,
                "elevate": 0,
                "originLat": 0.0,
                "originLng": 0.0,
                "originAlt": 0.0,
                "pilotLat": "0.0",
                "pilotLng": "0.0",
                "pilotAlt": "0.00",
                "centerLat": "0.0",
                "centerLng": "-0.1",
                "centerAlt": "0.00",
                "schedule": [schedule_category, schedule_name],
            },
            "scored": False,
            "scores": [
                0,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                600,
            ],
            "mans": fcmans.to_dict("records"),
            "data": fcdata.to_dict("records"),
        }

    def direction(self):
        """returns 1 for going right, -1 for going left"""
        return np.sign(self.att.transform_point(g.Point(1, 0, 0)).x)

    def cross_direction(self):
        """returns 1 for going out, -1 for coming in"""
        return np.sign(self.att.transform_point(g.Point(1, 0, 0)).y)

    def inverted(self) -> npt.NDArray:
        """returns true if the aircraft is inverted, false if upright"""
        return self.att.transform_point(g.Point(0, 0, 1)).z > 0

    def upright(self):
        return not self.inverted()

    def judging_itrans(self: State, template_itrans: g.Transformation):
        """The judging initial transform has its X axis in the states velocity vector and
        its wings aligned with the template"""
        return g.Transformation(
            self.pos[0],
            g.Quaternion.from_rotation_matrix(
                g.Coord.from_xy(
                    g.P0(),
                    self.att[0].transform_point(self.vel[0]),
                    template_itrans.att.transform_point(g.PY()),
                ).rotation_matrix()
            ).inverse(),
        )

    def move(self: State, transform: g.Transformation) -> State:
        """Move the state by a transformation"""
        return State.from_constructs(
            time=self.time,
            pos=transform.point(self.pos),
            att=transform.rotate(self.att),
            vel=self.vel,
            rvel=self.rvel,
            acc=self.acc,
        ).label(**self.labels)

    def move_back(self: State, transform: g.Transformation) -> State:
        self = self.move(g.Transformation(-transform.pos, g.Q0()))
        return self.move(g.Transformation(g.P0(), transform.att.inverse()))

    def relocate(self: State, start_pos: g.Point) -> State:
        offset = start_pos - self.pos[0]
        return self.move(g.Transformation(offset, g.Q0()))

    def superimpose_angles(
        self: State, angles: g.Point, reference: str = "body"
    ) -> State:
        assert reference in ["body", "world"]

        if reference == "body":
            rot = g.Quaternion.from_axis_angle(angles).inverse()
            return State.from_constructs(
                self.time,
                self.pos,
                self.att.body_rotate(angles),
                vel=rot.transform_point(self.vel),
                rvel=rot.transform_point(self.rvel)
                + angles.diff(self.dt),  # need to differentiate angles and add here
                acc=rot.transform_point(self.acc),
            ).label(**self.labels)
        else:
            att = self.att.rotate(angles)
            return State.from_constructs(
                self.time,
                self.pos,
                att,
                att.inverse().transform_point(self.att.transform_point(self.vel)),
                rvel=att.inverse().transform_point(
                    self.att.transform_point(self.rvel) + angles.diff(self.dt)
                ),
                acc=att.inverse().transform_point(self.att.transform_point(self.acc)),
            ).label(**self.labels)

    def superimpose_rotation(
        self: State, axis: g.Point, angle: float, reference: str = "body"
    ) -> State:
        """Generate a new section, identical to self, but with a continous rotation integrated"""
        t = self.time.t - self.time.t[0]
        rate = angle / self.time.t[-1]
        superimposed_rotation = t * rate

        angles = axis.unit().tile(len(t)) * superimposed_rotation

        return self.superimpose_angles(angles, reference)

    def superimpose_roll(self: State, angle: float) -> State:
        """Generate a new section, identical to self, but with a continous roll integrated

        Args:
            angle (float): the amount of roll to integrate
        """
        return self.superimpose_rotation(g.PX(), angle)

    def smooth_rotation(
        self: State,
        axis: g.Point,
        angle: float,
        reference: str = "body",
        w: float = 0.25,
        w2=0.1,
    ):
        """Accelerate for acc_prop * t, flat rate for middle, slow down for acc_prop * t.

        Args:
            axis (g.Point): Axis to rotate around.
            angle (float): angle to rotate.
            reference (selfr, optional): rotate about body or world. Defaults to "body".
            acc_prop (float, optional): proportion of total rotation to be accelerating for. Defaults to 0.1.
        """

        t = self.time.t - self.time.t[0]

        T = t[-1]

        V = angle / (T * (1 - 0.5 * w - 0.5 * w2))  # The maximum rate

        # between t=0 and t=wT
        x = t[t <= w * T]
        angles_0 = (V * x**2) / (2 * w * T)

        # between t=wT and t=T(1-w)
        y = t[(t > w * T) & (t <= (T - w2 * T))]
        angles_1 = V * y - V * w * T / 2

        # between t=T(1-w2) and t=T
        z = t[t > (T - w2 * T)] - T + w2 * T
        angles_2 = (
            V * z - V * z**2 / (2 * w2 * T) + V * T - V * w2 * T - 0.5 * V * w * T
        )

        angles = g.Point.full(axis.unit(), len(t)) * np.concatenate(
            [angles_0, angles_1, angles_2]
        )

        return self.superimpose_angles(angles, reference)

    def zero_g_acc(self):
        return self.att.inverse().transform_point(g.PZ(-9.81)) + self.acc

    def arc_centre(self) -> g.Point:
        acc = g.point.vector_rejection(self.zero_g_acc(), self.vel)
        with np.errstate(invalid="ignore"):
            return acc.unit() * abs(self.vel) ** 2 / abs(acc)

    def curvature(self, axis: g.Point) -> g.Point:
        """Returns the curvature of the path in 1/m, axis is the desired axial direction
        in the world frame"""
        trfl = self.to_track()

        po = g.point.vector_rejection(
            trfl.att.transform_point(
                trfl.zero_g_acc() * g.Point(0, 1, 1) / abs(trfl.u) ** 2
            ),
            axis,
        )
        return po

    #        po.data[-1, :] = np.nan
    #        return po.ffill()

    def F_gravity(self, mass: g.Mass):
        """Returns the gravitational force in N"""
        return mass.m * self.att.inverse().transform_point(g.PZ(-9.81))

    def F_inertia(self, mass: g.Mass):
        """Returns the inertial force in N"""
        return mass.m * (self.zero_g_acc() + g.Point.cross(self.rvel, self.vel))

    def M_inertia(self, mass: g.Mass):
        """return the inertial moment in N"""
        h = mass.angular_momentum(self.rvel)
        return h.diff(self.dt) + g.Point.cross(self.rvel, h)

    def get_rotation(self):
        return np.cumsum(g.Point.scalar_projection(self.rvel, self.vel) * self.dt)
