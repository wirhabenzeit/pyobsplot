import pathlib
import datetime
import anywidget
import traitlets
import pandas as pd
import polars as pl

from .data import pd_to_arrow, pl_to_arrow

bundler_output_dir = pathlib.Path("static")


class Obsplot(anywidget.AnyWidget):
    _esm = bundler_output_dir / "index.js"
    _css = bundler_output_dir / "index.css"
    spec = traitlets.Dict().tag(sync=True)

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0:
            spec = args[0]
        elif len(args) == 0 and len(kwargs) == 1 and "spec" in kwargs:
            spec = kwargs["spec"]
        elif len(args) == 0 and len(kwargs) > 0:
            spec = kwargs
        else:
            ValueError("Incorrect ObsPlot arguments")
        super().__init__(spec=spec)

    @traitlets.validate("spec")
    def _validate_spec(self, proposal):
        spec = proposal["value"]
        spec = parse_spec(spec)
        return spec


def parse_spec(spec):
    if spec is None:
        return None
    if isinstance(spec, list) or isinstance(spec, tuple):
        return [parse_spec(s) for s in spec]
    if (
        isinstance(spec, dict)
        and "type" in spec
        and spec["type"] == "FeatureCollection"
    ):
        return {"ipyobsplot-type": "GeoJson", "value": spec}
    if isinstance(spec, dict):
        return {k: parse_spec(v) for k, v in spec.items()}
    if isinstance(spec, pd.DataFrame):
        return {"ipyobsplot-type": "DataFrame", "value": pd_to_arrow(spec)}
    if isinstance(spec, pl.DataFrame):
        return {"ipyobsplot-type": "DataFrame", "value": pl_to_arrow(spec)}
    if isinstance(spec, datetime.date) or isinstance(spec, datetime.datetime):
        return {"ipyobsplot-type": "datetime", "value": spec.isoformat()}
    if (
        callable(spec)
        and isinstance(spec(), dict)
        and spec()["ipyobsplot-type"] == "function"
    ):
        out = spec()
        out["ipyobsplot-type"] = "function-object"
        return out
    return spec


class JSModule(type):
    def __getattr__(cls, name):
        def wrapper(*args, **kwargs):
            if kwargs:
                raise ValueError(
                    f"kwargs must not be passed to f{cls.__name__}.{name} : {kwargs}"
                )
            return {
                "ipyobsplot-type": "function",
                "module": cls.__name__,
                "method": name,
                "args": args,
            }

        return wrapper


class Plot(metaclass=JSModule):
    pass


class d3(metaclass=JSModule):
    pass


class Math(metaclass=JSModule):
    pass


def js(txt):
    return {"ipyobsplot-type": "js", "value": txt}
