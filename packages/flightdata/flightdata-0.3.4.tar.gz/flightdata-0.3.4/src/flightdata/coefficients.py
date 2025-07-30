from typing import ClassVar
from flightdata import Table, SVar, Constructs
from geometry import Point, P0
from dataclasses import dataclass


@dataclass(repr=False)
class Coefficients(Table):
    constructs: ClassVar[Constructs] = Table.constructs + Constructs([
        SVar("force", Point, ["cx", "cy", "cz"], None),
        SVar("moment", Point, ["cl", "cm", "cn"], None)
    ])

    @staticmethod
    def build(sec, q, consts):
        I = consts.mass.I[0]
        u = sec.vel
        du = sec.acc
        w = sec.rvel
        dw = sec.racc
        moment=P0(len(sec))#I*(dw + w.cross(w)) / (q * consts.s) 

        return Coefficients.from_constructs(
            sec.time,
            force=(du + w.cross(u)) * consts.mass.m[0] / (q * consts.s),
            moment=moment / Point(consts.b, consts.c, consts.b).tile(len(moment))
        )
