from datetime import datetime
from pydantic import BaseModel, Field
from pymongo import MongoClient

from car_cost.models.input_form_model import (
    InputFormModel,
    Financing,
    CarSpecs,
    Insurance,
    Energy,
    Usage,
    Discount,
    Taxes,
    Settings,
)
from car_cost.settings import DatabaseSettings


class QueriesModel(BaseModel):
    name: str
    financing: Financing
    car_specs: CarSpecs
    insurance: Insurance
    energy: Energy
    usage: Usage
    discount: Discount
    taxes: Taxes
    settings: Settings
    created_at: datetime = Field(default=datetime.now())


class Database:
    _settings: DatabaseSettings

    def __init__(self, settings: DatabaseSettings) -> None:
        self._settings = settings
        client = MongoClient(
            f"mongodb+srv://{self._settings.username}:{self._settings.password}@{self._settings.cluster_name}.1rypsqy.mongodb.net/?retryWrites=true&w=majority"
        )
        car_cost_db = client["car_cost"]
        self._queries_collection = car_cost_db["queries"]

    def _parse_query(self, query: InputFormModel) -> QueriesModel:
        assert isinstance(query.financing, Financing), (
            f"The value was an instance of {type(query.financing)} while the exepected"
            f" type was {Financing}"
        )
        return QueriesModel(
            name=query.name,
            financing=query.financing,
            car_specs=query.car_specs,
            insurance=query.insurance,
            energy=query.energy,
            usage=query.usage,
            discount=query.discount,
            taxes=query.taxes,
            settings=query.settings,
        )

    def add_query(self, query: InputFormModel) -> None:
        query_model = self._parse_query(query)
        self._queries_collection.insert_one(query_model.model_dump())
