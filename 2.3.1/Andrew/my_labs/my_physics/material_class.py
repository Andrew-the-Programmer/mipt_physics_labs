
from my_labs import PQ
import attr

@attr.define(kw_only=True)
class Material:
    dencity: PQ = attr.field()
