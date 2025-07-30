
from typing import ClassVar, overload, Literal
from flightdata import Table, SVar, Constructs, SVar, Flight, Origin
from geometry import Point, Base, PX, Euler, Time
import numpy as np
from dataclasses import dataclass

class Attack(Base):
    cols = ['alpha', 'beta', 'q']


@dataclass(repr=False)
class Flow(Table):
    constructs: ClassVar[Constructs] = Table.constructs + Constructs([
        SVar("aspd", Point, ["asx", "asy", "asz"], None),
        SVar("flow", Attack, ["alpha", "beta", "q"], None)
    ])

    @overload
    def __getattr__(self, key: Literal["aspd"]) -> Point: ...
    @overload
    def __getattr__(self, key: Literal["flow"]) -> Attack: ...

    def __getattr__(self, key):
        return super().__getattr__(key)

    @staticmethod
    def from_body(body, env):

        airspeed = body.vel - body.att.inverse().transform_point(env.wind)

        with np.errstate(invalid='ignore'):
            alpha =  np.arctan(airspeed.z / airspeed.x) 
        alpha[np.isnan(alpha)] = 0.0

        stab_airspeed = Euler(
            np.zeros(len(alpha)), 
            alpha, 
            np.zeros(len(alpha))
        ).transform_point(airspeed)
    
        with np.errstate(invalid='ignore'):
            beta = np.arctan(stab_airspeed.y / stab_airspeed.x)
        beta[np.isnan(beta)] = 0.0

        with np.errstate(invalid='ignore'):
            q = 0.5 * env.rho * abs(airspeed)**2
        q[np.isnan(q)] = 0.0
        
        return Flow.from_constructs(
            body.time, 
            airspeed,
            Attack(alpha, beta, q)
        )
    

    def rotate(self, coefficients, dclda, dcydb):
        new_flow = Attack(-coefficients.cz / dclda, -coefficients.cy / dcydb, self.flow.q)
        return Flow.from_constructs(coefficients.time, flow=new_flow, aspd=self.aspd)

    
    