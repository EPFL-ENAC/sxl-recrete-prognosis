import yaml
from typing import Union
import math
import numpy as np
import pandas as pd

VARIABLES_FILE_PATH = "variables.yml"


class MyConfig:
    """Get variables from yaml file and create attributes from them"""

    def __init__(self, data):
        self.__dict__.update(data)


def define_fsd_armamin(year: int) -> int:
    """Define the value of Fsd_armamin according to the year of construction.

    Parameters
    ----------
    year : int
        Construction year.

    Returns
    -------
    int
        fsd_armamin value.
    """

    if year == 1:
        fsd_armamin = 435000

    elif year == 2:
        fsd_armamin = 390000

    elif year == 3:
        fsd_armamin = 300000

    return fsd_armamin


def define_fyd(steelprofile_type: int) -> float:
    """Define the value of fyd according to the type of steel profile.

    Parameters
    ----------
    steelprofile_type : int
        Steel profile type.

    Raises
    ------
    ValueError
        Invalid steelprofile_type.

    Returns
    -------
    float
        fyd value.
    """

    # résistance profilé [N/mm2]
    if steelprofile_type == 1:
        fyd = 335 / 1.05

    # Résistance profilé de réemploi (pas acier de la meilleure qualité) [N/mm2]
    if steelprofile_type == 2:
        fyd = 335 / 1.05
    else:
        raise ValueError("Invalid steelprofile_type")

    return fyd


def read_data(steelprofile_type: int) -> pd.DataFrame:
    """Read data from excel file.

    Parameters
    ----------
    steelprofile_type : int
        Steel profile type.

    Returns
    -------
    pd.DataFrame
        Dataframe containing data from excel file.

    Raises
    ------
    ValueError
        Invalid steelprofile_type.
    """

    if steelprofile_type == 1:
        excel_file = "data_beams_1.xlsx"
        sheet_name = "1"
        # range_cells = 'B3:S29'
        skiprows = 2
        usecols = range(1, 19)
        nrows = 27

    elif steelprofile_type == 2:
        excel_file = "data_beams_casestudy.xlsx"
        sheet_name = "1"
        # range_cells = 'B4:S5'
        skiprows = 3
        usecols = range(1, 19)
        nrows = 2

    else:
        raise ValueError("Invalid steelprofile_type")

    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, usecols=usecols, skiprows=skiprows, nrows=nrows)
    return df


def processing(
    l0: float, l1: float, hsreuse=float, year=int, q0=int, q1=int, tpdist_beton_reuse=float, tpdist_metal_reuse=float
):
    # retrive variables from yaml file
    with open(VARIABLES_FILE_PATH, "r") as file:
        variables = yaml.safe_load(file)
    v = MyConfig(variables)

    # --------------------------------------------------------
    # caractérstiques du donneur
    Fsd_armamin = define_fsd_armamin(year)
    j = l1
    steelprofile_type = 2
    beamposition = 1

    # charge permanentes [kN/m2]
    Gslab0 = hsreuse * v.massevol_BA / 100

    # Inertie section par metre [mm4]
    Ibeton = ((hsreuse * 1000) ** 3) * 1000 / 12

    # --------------------------------------------------------
    # caractérstiques du receveur

    fyd = define_fyd(steelprofile_type=steelprofile_type)

    # --------------------------------------------------------
    ## données sur les profilés pour système 2
    # classés par W

    data = read_data(steelprofile_type=steelprofile_type)

    # masse linéaire des profilés utilisés dans les poutres[kN/m]
    profile_mass = data.iloc[:, 2] * 10**-3

    # Calculate profile_W - Wy des profilés utilisés dans les poutres [mm^3]
    profile_W = data.iloc[:, 3] * 10**3

    # Calculate profile_I - I des profilés utilisés dans les poutres [mm^4]
    profile_I = data.iloc[:, 4] * 10**6

    # Extract profile_hauteur - hauteur du profilé [mm]
    profile_hauteur = data.iloc[:, 1]

    # Extract profile_largeurtot - Largeur totale du profilé [mm]
    profile_largeurtot = data.iloc[:, 5]

    # Extract profile_degreasedsurf - [m^2/m] surface dégraissée et repeintre par mètre de poutre de réemploi -> PAS AUSSI LES NEUVES? VOIR Brütting et al.
    profile_degreasedsurf = data.iloc[:, 11]

    # Extract beam_sol - numero de poutres telles que listées dans "selection profiles.xls"
    beam_sol = data.iloc[:, 0]

    # Extract beam_vol_betonremplissage - aire du profilé [m^3/m]
    beam_vol_betonremplissage = data.iloc[:, 13]

    # Extract beam_welding - [m/m] mètre de soudure par mètre de poutre
    beam_welding = data.iloc[:, 12]

    # Extract beam_largeurentrepiece - [mm]
    beam_largeurentrepiece = data.iloc[:, 14]

    # Extract beam_caoutchoucwidth - [mm]
    beam_caoutchoucwidth = data.iloc[:, 17]

    # Extract supportingplates_mass  - masse de la plaque en acier pour les profilés de moins de 200mm de large [kN/m]
    supportingplates_mass = data.iloc[:, 10] * 10**-3
    beam_selfweight = None
    profile_unwelding = None
    profile_sandblastedsurf = None

    if steelprofile_type == 1:  # recycledsteel
        profile_unwelding = data.iloc[:, 15]  # [m/profilé] mètre à dé-souder pour démonter un profilé
        profile_sandblastedsurf = data.iloc[:, 16]  # [m2/m] surface sandblastée par mètre de profilé de réemploi

    if steelprofile_type == 2:  # reusedsteel
        profile_unwelding = data.iloc[:, 7]  # [m/profilé] mètre à dé-souder pour démonter un profilé
        profile_sandblastedsurf = data.iloc[:, 8]  # [m2/m] surface sandblastée par mètre de profilé de réemploi

    if beamposition == 1:  # belowconcrete
        beam_selfweight = 1.03  # facteur à rajouter à la charge sur les poutres liées à leur poids propre

    if beamposition == 2:  # concreteplane
        beam_selfweight = 1.1  # facteur à rajouter à la charge sur les poutres liées à leur poids propre

    profile_MRd = 0.7 * profile_W * fyd / 10**6  # MRd profilé kNm

    # --------------------------------------------------------
    # schéma de découpes
    # L_alpha, alpha*L0 doit grantir que Mrd_armamin0 > Med_1
    Qtotsurfacique1 = v.y_Gslab1 * Gslab0 + v.y_rev1 * v.Grev1 + v.y_Q1 * q1  # charge surfacique receveur [kN/m^2]
    Qtotsurfacique0 = v.y_Gslab0 * Gslab0 + v.y_rev0 * v.Grev0 + v.y_Q0 * q0  # charge surfacique donneur [kN/m^2]
    alpha = (Qtotsurfacique0 / Qtotsurfacique1 / 3) ** (1 / 2)

    # L_armamin
    if hsreuse < 0.18:
        r_barremin = 4 / 1000  # rayon d'une barre d'armature minimum [m]
    else:
        r_barremin = 5 / 1000  # rayon d'une barre d'armature minimum [m]

    Aire_barremin = math.pi * r_barremin**2  # aire d'une barre d'armature minimum [m^2]
    espa_barremin = 0.150  # espacement entre les barres d'armature minimum [m]
    n_barremin = 1 / espa_barremin  # nombre de barre d'armature par mètre linéaire [n/m]
    Aire_armamin = Aire_barremin * n_barremin  # aire de toutes les barres d'armatures par mètre [m^2]
    Mrd_armamin = (
        Aire_armamin * Fsd_armamin * 0.81 * hsreuse
    )  # moment résistant apporté par les armatures minimums et le béton [m^3]
    L_armamin = (Mrd_armamin * 8 / Qtotsurfacique1) ** (1 / 2) + 0.15  # +0.15 ok?

    # --------------------------------------------------------
    # données coffrage et étayage pour NEW (SYSTEM 0)
    # panneaux
    h_panneaux = 0.021  # [m] épaisseur des panneaux
    massesurf_panneaux = v.massevol_panneaux * h_panneaux  # [kg/m2] poids des panneaux horizontaux
    h_coffbord = 0.50  # hauteur du coffrage de bord [m]
    n_coffbord = 2  # nombre de coffrage de bord sur les bords long (aux appuis)
    masselin_coffbord = h_coffbord * h_panneaux * n_coffbord * v.massevol_panneaux  # [kg/m] poids des panneaux de bord
    n_uti_panneaux = 20  # [n] nombre d'utilisation des panneaux de coffrage en bois
    n_uti_chantier_panneaux = 2  # nombre d'utilisation sur le chantier des panneaux

    # poutrelles sous les panneaux
    masseline_1poutrelle = 4.7  # [kg/m] poids des poutrelles H20 doka
    quantite_poutrelles = 1 / 0.75 + 1 / 2.5  # [m/m2] quantité de poutrelles par m2 coffré --> A VERIFIER
    massesurf_poutrelles = masseline_1poutrelle * quantite_poutrelles  # [kg/m2] poids des poutrelles par m2 coffré
    n_uti_chantier_poutrelles = 2  # nombre d'utilisation sur le chantier des poutrelles

    # étais
    poidsunit_etai = 13  # [kg/étai]
    portee_etai = 2  # [m2/étai] surface d'influence sur un étai --> A VERIFIER
    masse_lin_etais = poidsunit_etai / portee_etai  # [kg/m2]
    n_uti_chantier_etais = 1.5  # nombre d'utilisation sur le chantier des étais

    # --------------------------------------------------------
    # données étayage pour le démontage avant REUSE (SYSTEM 1, 2A, 2B)
    poidsunit_etai = 13  # [kg/étai]
    portee_etai_reuse = 2  # [m2/étai] surface d'influence sur un étai
    masse_lin_etais_reuse = poidsunit_etai / portee_etai_reuse  # [kg/m2]

    # --------------------------------------------------------
    # schéma de sciage
    largcamion = 2.50  # largeur maximale de camion en Suisse selon l'art. 64-67 OCR

    # --------------------------------------------------------
    # caractéristique NEW
    tauxarmature_neuf = 0.014  # %taux d'armature dans béton neuf 1,4% -> estimé manuellement, voir "dalles neuves.xlsx"

    # --------------------------------------------------------
    # données LCA
    # distances
    tpdist_coffrageetayage = (
        120  # distance de transport du matériel de coffrage et étayage [km] (pour deux trajets) --> DISTANCE A VERIFIER
    )
    tpdist_metal = 60  # distance de transport des profilés métalliques [km] --> DISTANCE A VERIFIER
    tpdist_beton = 60  # distance de transport du béton [km] --> DISTANCE A VERIFIER
    tpdist_arma = 60  # distance de transport de l'acier d'armature [km] --> DISTANCE A VERIFIER

    # calculs pour impact levage selon la GRAVITE
    energrue_levage1kg1m = (
        v.ener_levage1kg1m / v.efficacitegrue
    )  # énergie utilisée par une grue pour lever 1 kg de 1m [J/m/kg]
    energrue_levage1kg = (
        energrue_levage1kg1m * v.hlevage / 1000000
    )  # énergie utilisée par une grue pour lever 1kg (inclut conversion de J à MJ) [MJ/kg]

    # calculs pour impact sciage
    kgco2_prodetelimi_disque = (
        v.vol_1disque * v.massevol_metal * v.kgco2_prodetelimi_acier / v.surfsciable_1disque
    )  # kgco2/m2 liée à l'usure du disque
    kgco2_prodetelimi_machine = (
        v.masse_1machine * v.kgco2_prod_machine * (1 + v.facteur_elimi_machine) / v.surfsciable_1machine
    )  # kgco2/m2 lié à l'usure de la machine

    # impacts carbone unitaires
    kgco2_levage = (
        energrue_levage1kg * v.kgco2_energiegrue
    )  # kgCO2/kg de matériel levé à la hauteur de construction selon GRAVITE -> néglige l'usure de la grue
    kgco2_sciage_beton = (
        kgco2_prodetelimi_disque + kgco2_prodetelimi_machine + v.kgco2_prodenergie_sciage
    )  # kgCO2/m2 pour le sciage du béton

    i = l0
    L_alpha = l0 * alpha

    # ------------------------------------------------------------------------------------------------------
    # IMPACT NEW (SYSTEM 0)
    # quantité béton armé neuf
    if l1 < 4:
        hsnew = 0.18  # hauteur de la dalle neuve [m]
    elif l1 < 6.5:
        hsnew = 0.20  # hauteur de la dalle neuve [m]
    else:
        hsnew = 0.22  # hauteur de la dalle neuve [m]

    volbeton = l1 * hsnew * (1 - tauxarmature_neuf)  # [m3/m]
    massebeton = volbeton * v.massevol_beton  # [kg/m]
    volarmature = l1 * hsnew * tauxarmature_neuf  # [m3/m]
    massearmature = volarmature * v.massevol_armature  # [kg/m]

    # impact de la production des panneaux de coffrage (sur 20 usages)
    masse_panneaux = l1 * massesurf_panneaux + masselin_coffbord  # [kg/m]
    impact_prod_coffr_new0 = v.kgco2_prod_panneauxcoffrage * masse_panneaux / n_uti_panneaux  # [kgco2/m2]

    # impact du transport des matériaux d'étayage et de coffrage
    masse_poutrelles = l1 * massesurf_poutrelles  # [kg/m] quantité de poutrelles sous étais
    masse_etais = l1 * masse_lin_etais  # [kg/m] quantité d'étais
    impact_tp_coffrageetayage_new0 = (
        v.kgco2_tp_camion3240t
        * tpdist_coffrageetayage
        * (
            masse_panneaux / n_uti_chantier_panneaux
            + masse_poutrelles / n_uti_chantier_poutrelles
            + masse_etais / n_uti_chantier_etais
        )
        / 1000
    )  # [kgco2/m2]

    # impact du levage et de la dépose des matériaux d'étayage et de coffrage
    impact_levageetdepose_coffrageetayage_new0 = kgco2_levage * (
        masse_panneaux / n_uti_chantier_panneaux
        + masse_poutrelles / n_uti_chantier_poutrelles
        + masse_etais / n_uti_chantier_etais
    )  # [kgco2/m]

    # impact de la production du béton
    impact_prod_betonneuf_new0 = v.kgco2_prod_beton * massebeton  # [kgco2/m]

    # impact du transport du béton
    impact_tp_betonneuf_new0 = v.kgco2_tp_camion3240t * massebeton / 1000 * tpdist_beton  # [kgco2/m]

    # impact de la production des armatures
    impact_prod_armaneuf_new0 = v.kgco2_prod_armature * massearmature  # [kgco2/m]

    # impact du transport des armatures
    impact_tp_armaneuf_new0 = v.kgco2_tp_camion3240t * tpdist_arma * massearmature / 1000  # [kgco2/m]

    # impact du levage des armatures
    impact_levage_armaneuf_new0 = kgco2_levage * massearmature  # [kgco2/m]

    # impact du levage du béton
    impact_levage_betonneuf_new0 = kgco2_levage * massebeton  # [kgco2/m]

    # impact du coulage du béton
    impact_coulage_betonneuf_new0 = v.kgco2_coulage_beton * volbeton  # [kgco2/m]

    # impact new
    impactnew_prod = (
        impact_prod_coffr_new0
        + impact_tp_coffrageetayage_new0
        + impact_levageetdepose_coffrageetayage_new0
        + impact_prod_betonneuf_new0
        + impact_tp_betonneuf_new0
        + impact_prod_armaneuf_new0
        + impact_tp_armaneuf_new0
        + impact_levage_armaneuf_new0
        + impact_levage_betonneuf_new0
        + impact_coulage_betonneuf_new0
    )  # [kgco2/m]

    # ------------------------------------------------------------------------------------------------------
    # IMPACT SYSTEM 1 - dalles simples uniquement (zones 1 et 3)
    if l1 <= L_armamin and l1 <= l0 or l1 <= L_alpha and l1 > L_armamin:  # conditions de la zone 1 et de la zone 3
        L_decoupeL0 = l1
        syst = 0
        Selection_beam_sol = 0

        # quantité béton armé de réemploi
        masselin_beton_reuse1 = l1 * hsreuse * v.massevol_BA  # masse BA dalle de réemploi par m [kg/m]

        # impact du transport des étais pour le donneur
        masse_etais_reuse1 = (
            masse_lin_etais_reuse * l1
        )  # [kg/m] quantité étais pour découpe donneur par mètre linéaire receveur
        impact_tp_etai_reuse1 = masse_etais_reuse1 / 1000 * tpdist_coffrageetayage * v.kgco2_tp_camion3240t  # [kgco2/m]

        # impact du levage et de la dépose des étais pour le donneur
        impact_levageeetdepose_etais_reuse1 = kgco2_levage * 2 * masse_etais_reuse1  # [kgco2/m]

        # impact du sciage du béton
        n_bloc_reuse1 = 1 / largcamion  # nombre de bloc de béton par mètre linéaire [n/m]
        surfsciage_reuse1 = ((n_bloc_reuse1 * l1) + 1) * 2 * hsreuse  # surface de béton sciée par mètre linéaire [m2/m]
        impact_sciage_betonreused_reuse1 = kgco2_sciage_beton * surfsciage_reuse1  # [kgco2/m]

        # impact de la dépose du béton
        impact_depose_betonreused_reuse1 = kgco2_levage * masselin_beton_reuse1  # [kgco2/m]

        # impact du transport du béton
        impact_tp_betonreused_reuse1 = (
            (masselin_beton_reuse1 / 1000) * tpdist_beton_reuse * v.kgco2_tp_camion3240t
        )  # [kgco2/m]

        # impact de la production des cornières métalliques
        hcorn = None
        epaisseurcorn = None

        if hsreuse == 0.14:  # hauteur de la cornière = largeur de la cornière = hauteur de la dalle de réemploi
            epaisseurcorn = 0.013  # épaisseur de la cornière selon la table des LNP (cornière la plus fine)
            hcorn = hsreuse
        elif hsreuse == 0.16:
            epaisseurcorn = 0.015
            hcorn = hsreuse
        elif hsreuse >= 0.18:
            epaisseurcorn = 0.016
            hcorn = hsreuse
        elif hsreuse == 0.20:
            epaisseurcorn = 0.016
            hcorn = hsreuse
        elif hsreuse == 0.22:
            epaisseurcorn = 0.016
            hcorn = 0.20

        volcormetal = hcorn * 2 * epaisseurcorn  # volume linéaire par cornière [m3/m/corniere]
        n_cor = 2
        qcorniere = 0.4  # longueur de cornière par mètre linéaire d'appui [m cornière /m]
        voltotcormetal = volcormetal * n_cor * qcorniere  # volume linéaire de métal pour les cornières [m3/m]
        massemetalcorn_reuse1 = voltotcormetal * v.massevol_metal  # masse linéaire de métal pour les cornières [kg/m]
        impact_prod_metalneuf_corn_reuse1 = massemetalcorn_reuse1 * v.kgco2_prod_profilmetal  # [kgco2/m]

        # impact de la production des plaques métalliques
        vol_1plaque = (
            0.25 * 0.15 * 0.008 + 3.14 * 0.008**2 * hsreuse * 4
        )  # volume par plaque avec boulons [m3/plaque]
        n_plaque_reuse1 = (2 + math.ceil(l1 / 2)) / largcamion  # nombre de plaque par mètre linéaire [plaque/m]
        massemetalplaque_reuse1 = (
            vol_1plaque * n_plaque_reuse1 * v.massevol_metal
        )  # volume linéaire de métal pour les plaques [kg/m]
        impact_prod_metalneuf_plaque_reuse1 = massemetalplaque_reuse1 * v.kgco2_prod_profilmetal  # [kgco2/m]

        # impact du transport des cornières métalliques
        impact_tp_metalneuf_corn_reuse1 = (
            massemetalcorn_reuse1 / 1000 * tpdist_metal * v.kgco2_tp_camion3240t
        )  # [kgco2/m]

        # impact du transport des plaques métalliques
        impact_tp_metalneuf_plaque_reuse1 = (
            massemetalplaque_reuse1 / 1000 * tpdist_metal * v.kgco2_tp_camion3240t
        )  # [kgco2/m]

        # impact de la production de la peinture protectrice
        surfacepeintparcorn = hcorn  # surface à peindre par m de cornière [m2/m]
        surfacepeinttot_reuse1 = (
            surfacepeintparcorn * n_cor * qcorniere
        )  # surface linéaire à peindre pour les cornières [m2/m]
        impact_prod_revpulvacier_reuse1 = v.kgco2_prod_revpulvacier * surfacepeinttot_reuse1  # [kgco2/m]

        # impact de la production du caoutchouc
        surfacecaoutchoucparcorn = (
            hcorn  # surface à peindre par m de cornière = surface à doubler par caoutchouc par m de cornière [m2/m]
        )
        volumecaoutchouctot_reuse1 = (
            surfacecaoutchoucparcorn * v.epaisseur_caoutchouc * n_cor * qcorniere
        )  # volume de caoutchouc pour doubler les cornières [m3/m]
        impact_prod_caoutchouc_reuse1 = (
            v.massevol_caoutchouc * volumecaoutchouctot_reuse1 * v.kgco2_prod_caoutchouc
        )  # impact de la production du caoutchouc [kgco2/m]

        # impact du dégraissage de l'acier
        impact_degraissage_metalneuf_reuse1 = v.kgco2_degraissage * surfacepeinttot_reuse1  # [kgco2/m]

        # impact du levage des cornières métalliques
        impact_levage_metalneuf_corn_reuse1 = kgco2_levage * massemetalcorn_reuse1  # [kgco2/m]

        # impact du levage des plaques métalliques
        impact_levage_metalneuf_plaque_reuse1 = kgco2_levage * massemetalplaque_reuse1  # [kgco2/m]

        # impact du levage du béton
        impact_levage_betonreused_reuse1 = kgco2_levage * masselin_beton_reuse1  # [kgco2/m]

        # impact du joint
        volumejointpoly = 0.02 * 0.02 * l1 / largcamion  # [m3/m]
        impact_prod_jointpolyneuf_reuse1 = v.kgco2_prod_jointpoly * v.massevol_jointpoly * volumejointpoly  # [kgco2/m]

        # impact du mortier dans les joints entre les pieces de beton
        volumemortier = (hsreuse - 0.03) * 0.02 * l1 / largcamion  # [m3/m]
        impact_prod_mortierneuf_reuse1 = volumemortier * v.massevol_mortier * v.kgco2_prod_mortier  # [kgco2/m]

        # impact EVITE de l'élimination du béton réutilisé
        impact_EVITE_elimi_betonreused_reuse1 = v.kgco2_elimi_beton * masselin_beton_reuse1  # [kgco2/m]

        # impact EVITE de l'élimination de l'acier d'armature réutilisé
        volarma0 = l1 * hsreuse * v.tauxarmature0  # volume des armatures réutilisées [m3/m]
        massearma0 = v.massevol_armature * volarma0  # masse des armatures réutilisées [m3/m]
        impact_EVITE_elimi_armareused_reuse1 = v.kgco2_elimi_armature * massearma0  # [kgco2/m]

        # impact réemploi
        impactreuse1 = (
            impact_tp_etai_reuse1
            + impact_levageeetdepose_etais_reuse1
            + impact_sciage_betonreused_reuse1
            + impact_depose_betonreused_reuse1
            + impact_tp_betonreused_reuse1
            + impact_levage_betonreused_reuse1
            + impact_prod_metalneuf_corn_reuse1
            + impact_prod_metalneuf_plaque_reuse1
            + impact_tp_metalneuf_corn_reuse1
            + impact_tp_metalneuf_plaque_reuse1
            + impact_degraissage_metalneuf_reuse1
            + impact_prod_revpulvacier_reuse1
            + impact_levage_metalneuf_plaque_reuse1
            + impact_levage_metalneuf_corn_reuse1
            + impact_prod_jointpolyneuf_reuse1
            + impact_prod_caoutchouc_reuse1
            + impact_prod_mortierneuf_reuse1
        )  # impact solution réemploi dalles simples [kgco2/m]

        # distribution des impacts (réemploi et new)
        impactreuse1_matrice = [
            impact_tp_etai_reuse1
            + impact_levageeetdepose_etais_reuse1
            + impact_depose_betonreused_reuse1
            + impact_levage_betonreused_reuse1
            + impact_tp_metalneuf_corn_reuse1
            + impact_tp_metalneuf_plaque_reuse1
            + impact_degraissage_metalneuf_reuse1
            + impact_levage_metalneuf_plaque_reuse1
            + impact_levage_metalneuf_corn_reuse1,
            impact_prod_revpulvacier_reuse1,
            impact_prod_jointpolyneuf_reuse1,
            +impact_prod_caoutchouc_reuse1,
            impact_prod_mortierneuf_reuse1,
            0,
            impact_prod_metalneuf_corn_reuse1,
            impact_prod_metalneuf_plaque_reuse1,
            0,
            0,
            0,
            impact_sciage_betonreused_reuse1,
            impact_tp_betonreused_reuse1,
            0,
        ]
        impact_levageetdepose_coffrageetetayage_new0 = 0  # to change !!!!!!

        impactnew1_matrice = [
            impact_tp_armaneuf_new0
            + impact_levage_armaneuf_new0
            + impact_levage_betonneuf_new0
            + impact_coulage_betonneuf_new0
            + impact_prod_coffr_new0
            + impact_tp_coffrageetayage_new0
            + impact_levageetdepose_coffrageetetayage_new0
            + impact_EVITE_elimi_armareused_reuse1,
            0,
            0,
            0,
            0,
            impact_prod_armaneuf_new0,
            0,
            0,
            0,
            impact_prod_betonneuf_new0,
            impact_tp_betonneuf_new0,
            0,
            0,
            impact_EVITE_elimi_betonreused_reuse1,
        ]

        # impactreuse = impactreuse1
        # impactreuse_m2[i, j] = impactreuse / L1

        # impactnew = impactnew_prod + impact_EVITE_elimi_betonreused_reuse1 + impact_EVITE_elimi_armareused_reuse1
        # impactnew_m2[i, j] = impactnew / L1

        # # DELTA NEW/REUSE
        # delta[i, j] = (impactnew - impactreuse) / impactnew
        # delta1[i, j] = (impactnew - impactreuse1) / impactnew
        # delta2[i, j] = 0
    else:
        # ------------------------------------------------------------------------------------------------------
        # IMPACT SYSTEM 2 - grille de poutres avec dalles simples (zones 2,4,5)
        impact_levageetdepose_coffrageetetayage_new0 = 0  # to change !!!!!!
        L_decoupeL0 = None

        if l0 <= L_armamin and l1 > l0:  # conditions de la zone 2
            L_decoupeL0 = l0
        elif (
            l1 > l0 and l0 > L_armamin or l1 <= l0 and l1 > L_alpha and l1 > L_armamin
        ):  # conditions de la zone 4 et de la zone 5
            L_decoupeL0 = max(L_alpha, L_armamin)

        if beamposition == 1:  # belowconcrete
            syst = 1

        Qlin = L_decoupeL0 * Qtotsurfacique1 * beam_selfweight  # [kN/m]

        # SELECTION PROFILE - SELECTIONS CARACT. A COMPLETER
        Med = Qlin * (l1**2) / 8  # Nmm
        ind = np.where(profile_MRd > Med)[0]

        Selection_I = profile_I[np.min(ind)]
        Selection_beam_largeurentrepiece = beam_largeurentrepiece[np.min(ind)]

        test = 0
        it = 0
        flechemax_freq = l1 * 1000 / 350  # mm
        flechemax_perm = l1 * 1000 / 300  # mm
        sel = np.min(ind)

        while test < 2:
            test = 0
            flecheBeam_freq = (
                (L_decoupeL0 + Selection_beam_largeurentrepiece / 1000)
                * q1
                * (l1 * 1000) ** 4
                / v.profileE
                / (Selection_I)
                * 5
                / 384
            )  # mm
            flecheBeton_freq = q1 * (L_decoupeL0 * 1000) ** 4 / v.Ebeton / Ibeton * 5 / 384  # mm
            flechetot_freq = flecheBeam_freq + flecheBeton_freq
            if flechetot_freq <= flechemax_freq:
                test = test + 1
            else:
                it = it + 1
                sel = np.min(ind) + it
                Selection_I = profile_I[sel]
                Selection_beam_largeurentrepiece = beam_largeurentrepiece[sel]
            if steelprofile_type == 2:  # reusedsteel
                flecheBeam_perm_reuse = (
                    (L_decoupeL0 + Selection_beam_largeurentrepiece / 1000)
                    * (Gslab0 + v.Grev1 + v.Psi_1 * q1)
                    * (l1 * 1000) ** 4
                    / v.profileE
                    / (Selection_I)
                    * 5
                    / 384
                )  # mm
                flecheBeton_perm = (
                    (Gslab0 + v.Grev1 + v.Psi_1 * q1) * (L_decoupeL0 * 1000) ** 4 / v.Ebeton / Ibeton * 5 / 384
                )  # mm
                flechetot_perm_reuse = flecheBeam_perm_reuse + flecheBeton_perm
                if flechetot_perm_reuse <= flechemax_perm:
                    test = test + 1
                else:
                    it = it + 1
                    sel = np.min(ind) + it
                    Selection_I = profile_I[sel]
                    Selection_beam_largeurentrepiece = beam_largeurentrepiece[sel]
            else:
                test = test + 1

        Selection_W = profile_W[sel]
        Selection_I = profile_I[sel]
        Selection_profile_mass = profile_mass[sel]
        Selection_profile_hauteur = profile_hauteur[sel]
        Selection_profile_largeurtot = profile_largeurtot[sel]
        Selection_profile_degreasedsurf = profile_degreasedsurf[sel]
        Selection_beam_sol = beam_sol[sel]
        Selection_beam_welding = beam_welding[sel]
        Selection_supportingplates_mass = supportingplates_mass[sel]
        Selection_profile_unwelding = profile_unwelding[sel]
        Selection_profile_sandblastedsurf = profile_sandblastedsurf[sel]
        Selection_beam_largeurentrepiece = beam_largeurentrepiece[sel]
        Selection_beam_vol_betonremplissage = beam_vol_betonremplissage[sel]
        Selection_beam_caoutchoucwidth = beam_caoutchoucwidth[sel]

        # sol[i, j] = Selection_beam_sol

        # ------------------------------------------------------------------------------------------------------
        ## IMPACTS COMMON TO ALL SYSTEMS 2
        # Ratio slab:beam
        qdalle = None
        if beamposition == 1:  # belowconcrete
            qdalle = 1
        if beamposition == 2:  # concrete plane
            qdalle = 1 / (L_decoupeL0 + Selection_beam_largeurentrepiece / 1000) * L_decoupeL0

        # Quantity of metal for metal plates
        vol_1plaque = 0.2 * 0.15 * 0.01 + 3.14 * 0.008**2 * hsreuse * 4  # volume per plate with bolts [m3/plaque]
        n_plaque_reuse2 = (
            (2 * math.ceil(l1 / largcamion) + math.ceil(L_decoupeL0 / 1.5)) / L_decoupeL0 * qdalle
        )  # number of plates per linear meter [plaque/m]
        massemetalplaque_reuse2 = (
            vol_1plaque * n_plaque_reuse2 * v.massevol_metal
        )  # linear mass of metal for plates [kg/m]

        # Sawn concrete surface
        n_bloc_reuse2 = math.ceil(l1 / largcamion)  # number of blocks required to cover L1
        surfsciage_reuse2 = (
            (l1 / L_decoupeL0 * 2 + (n_bloc_reuse2 * 2)) * hsreuse * qdalle
        )  # sawn concrete surface per linear meter [m2/m]

        # Impact of transporting props for the donor
        masse_etais_reuse2 = (
            masse_lin_etais_reuse * l1 * qdalle
        )  # quantity of props for donor cutting per linear meter receiver
        impact_tp_etais_reuse2 = (
            masse_etais_reuse2 / 1000 * tpdist_coffrageetayage * v.kgco2_tp_camion3240t
        )  # [kgco2/m]

        # Impact of lifting and removing props
        impact_levageetdepose_etais_reuse2 = kgco2_levage * masse_etais_reuse2  # [kgco2/m]

        # Impact of concrete sawing
        impact_sciage_betonreused_reuse2 = kgco2_sciage_beton * surfsciage_reuse2  # [kgco2/m]

        # Impact of the joint between concrete pieces
        volumejointpoly2 = 0.02 * 0.02 * n_bloc_reuse2  # [m3/m]
        impact_prod_jointpolyneuf_reuse2 = (
            v.kgco2_prod_jointpoly * v.massevol_jointpoly * volumejointpoly2 * qdalle
        )  # [kgco2/m]

        # Impact of mortar in joints between concrete pieces
        volumemortier2 = (hsreuse - 0.03) * 0.02 * n_bloc_reuse2  # [m3/m]
        impact_prod_mortierneuf_reuse2 = (
            volumemortier2 * v.massevol_mortier * v.kgco2_prod_mortier * qdalle
        )  # [kgco2/m]

        # Quantity of metal for beams
        qpoutreparmlin = 1 / (
            L_decoupeL0 + (Selection_beam_largeurentrepiece / 1000)
        )  # average number of beams per meter (in width) of the floor
        masselin_poutre = (
            qpoutreparmlin * Selection_profile_mass * 100 * l1
        )  # average metal mass per linear meter of the floor [kg/m]

        # Quantité de béton de réemploi
        lbetonparmlin = 1 - (
            (Selection_beam_largeurentrepiece / 1000) * qpoutreparmlin
        )  # Longueur de béton par m linéaire [m/m] A VERIFIER
        masselin_beton_reuse2 = l1 * hsreuse * lbetonparmlin * v.massevol_BA  # Masse BA dalle de réemploi par m [kg/m]

        # Impact pour la dépose au sol (//levage) du béton scié
        impact_depose_betonreused_reuse2 = kgco2_levage * masselin_beton_reuse2  # [kgco2/m]

        # Impact du transport du béton
        impact_tp_betonreused_reuse2 = (
            masselin_beton_reuse2 / 1000 * tpdist_beton_reuse * v.kgco2_tp_camion3240t
        )  # [kgco2/m]

        # Impact du levage du béton
        impact_levage_betonreused_reuse2 = kgco2_levage * masselin_beton_reuse2  # [kgco2/m]

        # Quantité de métal pour les cornières pour appuyer les poutres A CORRIGER
        masse_corn2 = v.masse_lin_corn2 * Selection_profile_largeurtot / 1000 * 2 * qpoutreparmlin  # [kg/m]

        # Impact de la production des cornières métalliques
        impact_prod_metalneuf_corn_reuse2 = masse_corn2 * v.kgco2_prod_profilmetal

        # Impact de la production des plaques métalliques
        impact_prod_metalneuf_plaque_reuse2 = massemetalplaque_reuse2 * v.kgco2_prod_profilmetal

        # Impact du transport des plaques métalliques
        impact_tp_metalneuf_plaque_reuse2 = massemetalplaque_reuse2 / 1000 * tpdist_metal * v.kgco2_tp_camion3240t

        # Impact du transport des cornières métalliques
        impact_tp_metalneuf_corn_reuse2 = masse_corn2 / 1000 * tpdist_metal * v.kgco2_tp_camion3240t

        # Impact des soudures sur l'acier
        impact_welding_reuse2 = Selection_beam_welding * l1 * qpoutreparmlin * v.kgco2_welding

        # Impact du dégraissage de l'acier
        surface_peint_1beam = Selection_profile_degreasedsurf  # FACTEUR 1/1000 enlevé!
        surfacepeinttot_reuse2 = (
            surface_peint_1beam * qpoutreparmlin * l1
        )  # Surface à protéger avec peinture ignifuge par mètre linéaire de plancher[m2/m]
        impact_degraissage_metalneuf_reuse2 = v.kgco2_degraissage * surfacepeinttot_reuse2

        # Impact de la production de la peinture protectrice
        impact_prod_revpulvacier_reuse2 = v.kgco2_prod_revpulvacier * surfacepeinttot_reuse2

        # Impact de la production du caoutchouc
        volumecaoutchouctot_reuse2 = (
            Selection_beam_caoutchoucwidth / 1000 * l1 * qpoutreparmlin * v.epaisseur_caoutchouc
        )  # Volume de caoutchouc par mètre lin de plancher [m3/m]
        impact_prod_caoutchouc_reuse2 = (
            v.massevol_caoutchouc * volumecaoutchouctot_reuse2 * v.kgco2_prod_caoutchouc
        )  # Impact de la production du caoutchouc [kgco2/m]

        # Impact du levage des cornières métalliques
        impact_levage_metalneuf_corn_reuse2 = kgco2_levage * masse_corn2  # [kgco2/m]

        # Impact du levage des plaques métalliques
        impact_levage_metalneuf_plaque_reuse2 = kgco2_levage * massemetalplaque_reuse2  # [kgco2/m]

        # Impact EVITE de l'élimination du béton réutilisé
        impact_EVITE_elimi_betonreused_reuse2 = v.kgco2_elimi_beton * masselin_beton_reuse2  # [kgco2/m]

        # Impact EVITE de l'élimination de l'acier d'armature réutilisé !!! A CORRIGER !!!
        volarma0 = l1 * hsreuse * lbetonparmlin * v.tauxarmature0  # Volume des armatures réutilisées [m3/m]
        massearma0 = v.massevol_armature * volarma0  # Masse des armatures réutilisées [kg/m]
        impact_EVITE_elimi_armareused_reuse2 = v.kgco2_elimi_armature * massearma0  # [kgco2/m]

        # ------------------------------------------------------------------------------------------------------
        ## IMPACTS SPECIAUX POUR SYSTEMES 2 AVEC PROFILES NEUFS
        if steelprofile_type == 1:  # recycledsteel
            # impact de la production des profilés métalliques
            impact_prod_metalneuf_profiles_reuse2 = masselin_poutre * v.kgco2_prod_profilmetal

            # impact du transport des profilés métalliques
            impact_tp_metalneuf_profiles_reuse2 = masselin_poutre / 1000 * tpdist_metal * v.kgco2_tp_camion3240t

            # impact du levage des profillés métalliques
            impact_levage_metalneuf_profiles_reuse2 = kgco2_levage * masselin_poutre
        elif steelprofile_type == 2:  # reusedsteel
            impact_prod_metalneuf_profiles_reuse2 = 0
            impact_tp_metalneuf_profiles_reuse2 = 0
            impact_levage_metalneuf_profiles_reuse2 = 0

        # ------------------------------------------------------------------------------------------------------
        ## IMPACTS SPECIAUX POUR SYSTEMES 2 AVEC PROFILES REEMPLOI
        if steelprofile_type == 1:  # recycledsteel
            impact_unwelding_metalreuse_reuse2 = 0
            impact_depose_metalreused_reuse2 = 0
            impact_sablage_metalreused_reuse2 = 0
            impact_tp_metalreused_reuse2 = 0
            impact_EVITE_elimi_metalreused_reuse2 = 0
        elif steelprofile_type == 2:  # reusedsteel
            # impact de l'ouverture/unwelding connections sur le donneur
            impact_unwelding_metalreuse_reuse2 = (
                Selection_profile_unwelding * qpoutreparmlin * v.kgco2_welding
            )  # [kgco2/m]

            # impact de la dépose des profilés de réemploi
            impact_depose_metalreused_reuse2 = kgco2_levage * masselin_poutre  # [kgco2/m]

            # impact du sablage des profilés
            impact_sablage_metalreused_reuse2 = (
                Selection_profile_sandblastedsurf * l1 * qpoutreparmlin * v.kgco2_sandblasting
            )  # [kgco2/m]

            # impact du transport des profilés de réemploi
            impact_tp_metalreused_reuse2 = (
                masselin_poutre / 1000 * tpdist_metal_reuse * v.kgco2_tp_camion3240t
            )  # [kgco2/m]

            # impact EVITE de l'élimination des profilés métalliques réutilisés
            impact_EVITE_elimi_metalreused_reuse2 = masselin_poutre * v.kgco2_elimi_profilmetal  # [kgco2/m]

        # ------------------------------------------------------------------------------------------------------
        ## IMPACTS SPECIAUX POUR SYSTEMS 2 AVEC PROFILES DANS LE PLAN DU BETON -> RAJOUTER LA PROD ET LE TP DU BETON DANS LES PROFILES!
        if beamposition == 1:  # belowconcrete
            impact_prod_betonnew_reuse2 = 0
            impact_tp_betonnew_reuse2 = 0
        elif beamposition == 2:  # concreteplan
            if Selection_profile_hauteur / 1000 <= hsreuse:
                masse_betonremplissage_complement = (
                    hsreuse - Selection_profile_hauteur / 1000 * Selection_profile_largeurtot / 1000
                )
            if Selection_profile_hauteur / 1000 > hsreuse:
                masse_betonremplissage_complement = (Selection_profile_hauteur / 1000 - hsreuse) * 0.2
            masse_betonremplissage_tot = (
                (Selection_beam_vol_betonremplissage + masse_betonremplissage_complement)
                * qpoutreparmlin
                * v.massevol_beton
                * l1
            )  # [m3/m de poutre]*[kg/m3]*[qpoutre/m]
            impact_prod_betonnew_reuse2 = masse_betonremplissage_tot * v.kgco2_prod_beton
            impact_tp_betonnew_reuse2 = masse_betonremplissage_tot / 1000 * v.kgco2_tp_camion3240t * tpdist_beton

        impactreuse2 = (
            impact_tp_etais_reuse2
            + impact_levageetdepose_etais_reuse2
            + impact_sciage_betonreused_reuse2
            + impact_depose_betonreused_reuse2
            + impact_tp_betonreused_reuse2
            + impact_levage_betonreused_reuse2
            + impact_prod_jointpolyneuf_reuse2
            + impact_prod_caoutchouc_reuse2
            + impact_prod_mortierneuf_reuse2
            + impact_prod_metalneuf_corn_reuse2
            + impact_prod_metalneuf_plaque_reuse2
            + impact_tp_metalneuf_plaque_reuse2
            + impact_tp_metalneuf_corn_reuse2
            + impact_levage_metalneuf_corn_reuse2
            + impact_levage_metalneuf_plaque_reuse2
            + impact_welding_reuse2
            + impact_degraissage_metalneuf_reuse2
            + impact_prod_revpulvacier_reuse2
            + impact_prod_metalneuf_profiles_reuse2
            + impact_tp_metalneuf_profiles_reuse2
            + impact_levage_metalneuf_profiles_reuse2
            + impact_unwelding_metalreuse_reuse2
            + impact_depose_metalreused_reuse2
            + impact_tp_metalreused_reuse2
            + impact_sablage_metalreused_reuse2
            + impact_prod_betonnew_reuse2
            + impact_tp_betonnew_reuse2
        )
        impactreuse = impactreuse2

        impactnew = (
            impactnew_prod
            + impact_EVITE_elimi_betonreused_reuse2
            + impact_EVITE_elimi_armareused_reuse2
            + impact_EVITE_elimi_metalreused_reuse2
        )

        impactreuse2_matrice = [
            impact_tp_etais_reuse2
            + impact_levageetdepose_etais_reuse2
            + impact_depose_betonreused_reuse2
            + impact_levage_betonreused_reuse2
            + impact_tp_metalneuf_plaque_reuse2
            + impact_tp_metalneuf_corn_reuse2
            + impact_levage_metalneuf_corn_reuse2
            + impact_levage_metalneuf_plaque_reuse2
            + impact_welding_reuse2
            + impact_degraissage_metalneuf_reuse2
            + impact_tp_metalneuf_profiles_reuse2
            + impact_levage_metalneuf_profiles_reuse2
            + impact_unwelding_metalreuse_reuse2
            + impact_depose_metalreused_reuse2
            + impact_tp_metalreused_reuse2
            + impact_sablage_metalreused_reuse2
            + impact_prod_betonnew_reuse2
            + impact_tp_betonnew_reuse2,
            impact_prod_revpulvacier_reuse2,
            impact_prod_jointpolyneuf_reuse2,
            impact_prod_caoutchouc_reuse2,
            impact_prod_mortierneuf_reuse2,
            0,
            impact_prod_metalneuf_corn_reuse2,
            impact_prod_metalneuf_plaque_reuse2,
            impact_prod_metalneuf_profiles_reuse2,
            0,
            0,
            impact_sciage_betonreused_reuse2,
            impact_tp_betonreused_reuse2,
            0,
        ]
        impactnew2_matrice = [
            impact_EVITE_elimi_armareused_reuse2
            + impact_EVITE_elimi_metalreused_reuse2
            + impact_prod_coffr_new0
            + impact_tp_coffrageetayage_new0
            + impact_levageetdepose_coffrageetetayage_new0
            + impact_tp_armaneuf_new0
            + impact_levage_armaneuf_new0
            + impact_levage_betonneuf_new0
            + impact_coulage_betonneuf_new0,
            0,
            0,
            0,
            0,
            impact_prod_armaneuf_new0,
            0,
            0,
            0,
            impact_prod_betonneuf_new0,
            impact_tp_betonneuf_new0,
            0,
            0,
            impact_EVITE_elimi_betonreused_reuse2,
        ]

        delta = (impactnew - impactreuse) / impactnew
        delta1 = 0
        delta2 = (impactnew - impactreuse2) / impactnew


        bar_char_data = pd.DataFrame({'lab': ["Impact new", "Impact reuse", "Impact reuse 2"],'val': [impactnew, impactreuse, impactreuse2]})
        bar_char_data.set_index('lab', inplace=True)


        labels = [
            "Category 1",
            "Category 2",
            "Category 3",
            "Category 4",
            "Category 5",
            "Category 6",
            "Category 7",
            "Category 8",
            "Category 9",
            "Category 10",
            "Category 11",
            "Category 12",
            "Category 13",
            "Category 14",
        ]

        drawing = {}
        drawing["l1"] = l1
        drawing["h"] = hsreuse
        drawing["number_part"] = 2


        pie_chart_data = pd.DataFrame({'lab': labels,'val':impactnew2_matrice})

       
        return [bar_char_data,pie_chart_data,drawing]



if __name__ == "__main__":
    l0 = 3
    l1 = 6
    hsreuse = 0.15
    year = 2
    q0 = 2
    q1 = 2
    tpdist_beton_reuse = 20
    tpdist_metal_reuse = 80

    result = processing(
        l0=l0,
        l1=l1,
        hsreuse=hsreuse,
        year=year,
        q0=q0,
        q1=q1,
        tpdist_beton_reuse=tpdist_beton_reuse,
        tpdist_metal_reuse=tpdist_metal_reuse,
    )

    print(result[0])
