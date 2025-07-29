import logging

from openfisca_core import periods
from openfisca_core.parameters import Parameter
from openfisca_core.reforms import Reform

from leximpact_dotations_back.computing.dotations_simulation import DotationsSimulation


# configure _root_ logger
logger = logging.getLogger()

REFORM_YEAR = 2024


def get_openfisca_parameter(parameters, parameter_dot_name) -> Parameter | None:
    try:
        parameter_name = parameter_dot_name
        cles = parameter_name.split('.')

        for cle in cles:
            parameters = parameters.children[cle]

        logger.debug(f"La valeur correspondante à '{parameter_name}' est : {parameters}")
        return parameters  # un Parameter si parameter_dot_name indique bien une feuille de l'arbre des parameters

    except KeyError:
        # La clé '{cle}' n'a pas été trouvée dans modèle
        logger.error(f"Paramètre '{parameter_name}' introuvable.")
        return None
    except AttributeError:
        logger.error("La structure du modèle n'est pas un dictionnaire à un niveau donné.")
        return None


def reform_parameters_from_amendement(parameters):
    reform_period = periods.period(REFORM_YEAR)
    amendement_parameters = {
        "dotation_solidarite_rurale.seuil_nombre_habitants": 5000,
        "dotation_solidarite_rurale.augmentation_montant": 100_000_000
    }

    for parameter_name, value in amendement_parameters.items():

        try:
            one_parameter: Parameter = get_openfisca_parameter(parameters, parameter_name)
            if one_parameter is not None:
                one_parameter.update(period=reform_period, value=value)
        except ValueError as e:
            logger.warning(f"[Amendement] Échec de la réforme du paramètre '{parameter_name}': {e}")

    return parameters


class reform_from_amendement(Reform):
    name = 'Amendement'

    def apply(self):
        self.modify_parameters(modifier_function=reform_parameters_from_amendement)


def reform_parameters_from_plf(parameters):
    reform_period = periods.period(REFORM_YEAR)
    plf_parameters = {
        "dotation_solidarite_rurale.seuil_nombre_habitants": 7000,
        "dotation_solidarite_rurale.augmentation_montant": 50_000_000
    }

    for parameter_name, value in plf_parameters.items():

        try:
            one_parameter: Parameter = get_openfisca_parameter(parameters, parameter_name)
            if one_parameter is not None:
                one_parameter.update(period=reform_period, value=value)
        except ValueError as e:
            logger.warning(f"[PLF] Échec de la réforme du paramètre '{parameter_name}': {e}")

    return parameters


class reform_from_plf(Reform):
    name = 'PLF'

    def apply(self):
        self.modify_parameters(modifier_function=reform_parameters_from_plf)


def get_reformed_dotations_simulation(
        reform_model,
        data_directory,
        year_period
) -> DotationsSimulation:

    dotations_simulation = DotationsSimulation(
        data_directory=data_directory,  # TODO optimiser en évitant le retraitement de criteres et adapted_criteres
        model=reform_model,
        annee=year_period
    )

    return dotations_simulation
