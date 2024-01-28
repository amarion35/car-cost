from typing import Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

EngineType = Literal[
    "Diesel", "Essence", "Hybride", "Hybride Rechargeable", "Electrique", "GPL"
]


class Financing(BaseModel):
    price: int = Field(
        alias="Prix", description="Prix d'achat du véhicule", default=35000
    )
    eco_bonus: int = Field(alias="Bonus écologique", default=5000)
    resell: int = Field(
        alias="Revente ancien véhicule ou prime à la conversion", default=2500
    )
    loan: int = Field(alias="Montant emprunté", default=20000)
    loan_rate: float = Field(alias="Taux d'emprunt en %", default=5)
    loan_duration: int = Field(alias="Durée d'emprunt en années", default=6)


class CarSpecs(BaseModel):
    engine_type: EngineType = Field(
        alias="Motorisation", description="Type de moteur", default="Electrique"
    )
    administrative_power: int = Field(alias="Puissance fiscale (CV)", default=4)
    fuel_consumption: float = Field(
        alias="Consommation sur 100km",
        description="Consommation du véhicule sur 100km en litres ou kwh",
        default=16.4,
    )
    maintenance_cost: int = Field(
        alias="Coût annuel maintenance",
        description="Coût annuel de la maintenance",
        default=150,
    )


class Insurance(BaseModel):
    insurance_cost: int = Field(
        alias="Coût annuel assurance",
        description="Coût annuel de l'assurance",
        default=700,
    )


class Energy(BaseModel):
    fuel_cost: float = Field(
        alias="Prix du carburant (/L ou /kWh)",
        description=(
            "Prix du carburant (au litre ou au kwh pour les véhicules électriques)"
        ),
        default=0.227,
    )


class Usage(BaseModel):
    distance_personal: int = Field(
        alias="Distance personnel (km/an)",
        description=(
            "Distance parcourue avec le véhicule en km par an dans le cadre personnel"
        ),
        default=4000,
    )
    distance_work: int = Field(
        alias="Distance professionnelle (km/an)",
        description=(
            "Distance parcourue avec le véhicule en km par an dans le cadre"
            " professionel"
        ),
        default=7600,
    )


class Discount(BaseModel):
    initial_value: int = Field(
        alias="Valeur à la revente initiale",
        description=(
            "La valeur initiale du véhicule à la revente peut être différente du prix"
            " d'achat. C'est le cas par exemple lors de l'achat d'un véhicule neuf ou"
            " si le véhicule a été acheté avec une sur-cote ou une sous-cote. Cette"
            " valeur peut être estimé en consultant les sites d'annonces d'occasion ou"
            " estimant la côte gratuitement sur des sites spécialisés."
        ),
        default=28000,
    )
    value_at_5_years: int = Field(
        alias="Valeur à la revente estimée dans 5 ans",
        description=(
            "Cette valeur peut être estimé en consultant les sites d'annonces"
            " d'occasion ou estimant la côte gratuitement sur des sites spécialisés."
        ),
        default=15000,
    )


class Taxes(BaseModel):
    taxable_revenue: int = Field(
        alias="Revenus imposables",
        description=(
            "Permet de prendre en compte l'abattement lié à la déduction des frais"
            " réels."
        ),
        default=30000,
    )


class Settings(BaseSettings):
    n_years: int = Field(alias="Nombre d'années", default=10)
    share_data: bool = Field(alias="J'accepte de partager ces données", default=True)


class InputFormModel(BaseModel):
    name: str = Field(alias="Nom", description="Nom du profil", default="Peugeot e208")
    financing: Financing = Field(alias="Financement")
    car_specs: CarSpecs = Field(alias="Specifications du véhicule")
    insurance: Insurance = Field(alias="Assurance")
    energy: Energy = Field(alias="Energie")
    usage: Usage = Field(alias="Utilisation")
    discount: Discount = Field(alias="Décote")
    taxes: Taxes = Field(alias="Fiscalité")
    settings: Settings = Field(alias="Paramètres")
