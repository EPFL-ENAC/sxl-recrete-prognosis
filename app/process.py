import math
import os

import numpy as np
import pandas as pd
import yaml

VARIABLES_FILE_PATH = os.path.join(os.path.dirname(__file__), "variables.yml")
BEAMS_CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "data_beams_1.xlsx")


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
    """Define the value of fyd (steel profile yield strength)
    according to the type of steel profile (reuse S235, new S355).


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
    # New steel profile yield strength [N/mm2]
    if steelprofile_type == 1:
        fyd = 355 / 1.05

    # Reuse steel profile yield strength (conservative asumption of low yield strength) [N/mm2]
    elif steelprofile_type == 2:
        fyd = 235 / 1.05
    else:
        raise ValueError("Invalid steelprofile_type")

    return fyd


def read_data_beams() -> pd.DataFrame:
    """Read data from Excel file with Swiss steel profiles.

    Parameters
    ----------
    Returns
    -------
    pd.DataFrame
        Dataframe containing data from excel file.

    """
    sheet_name = "1"
    skiprows = 2
    usecols = range(0, 19)
    nrows = 27

    df = pd.read_excel(
        BEAMS_CONFIG_FILE_PATH,
        sheet_name=sheet_name,
        header=None,
        usecols=usecols,
        skiprows=skiprows,
        nrows=nrows,
    )

    return df


def get_beam_name(row_id: int) -> str:
    """Return steel-profile name from the Excel file.
    Parameters
    ----------
    row_id : int
        Row id.

    Returns
    -------
    str
        Name of the beam.
    """
    df = read_data_beams()
    return df.iloc[row_id, 0]


def get_profile_data(steelprofile_type: int, beamposition: int, fyd: float) -> tuple:
    """Return steel profile data from the configuration Excel file chosen according to the steel profile type.

    Parameters
    ----------
    steelprofile_type : int
        Steel profile type.
    beamposition : int
        Beam position.
    fyd : float
        Steel yield strength based on steel profile type

    Returns
    -------
    tuple
        Values for : profile_mass, profile_W, profile_I, profile_hauteur, profile_largeurtot, profile_degreasedsurf,
        beam_sol, beam_vol_betonremplissage, beam_welding, beam_largeurentrepiece, beam_caoutchoucwidth,
        supportingplates_mass, beam_selfweight, profile_unwelding, profile_sandblastedsurf,profile_MRd

    """

    data = read_data_beams()

    beam_name = data.iloc[:, 0]

    # Linear mass of steel profiles[kN/m]
    profile_mass = data.iloc[:, 3] * 10**-3

    # Plastic section modulus W of steel profiles [mm^3]
    profile_W = data.iloc[:, 4] * 10**3

    # Inertia Iy of steel profiles [mm^4]
    profile_I = data.iloc[:, 5] * 10**6

    # Height of steel profiles [mm]
    profile_hauteur = data.iloc[:, 2]

    # Width of steel profiles [mm]
    profile_largeurtot = data.iloc[:, 6]

    # Surface to degrease and paint of steel profiles per linear meter [m^2/m]
    # Warning: only for reused steel profiles !!
    profile_degreasedsurf = data.iloc[:, 12]

    # Steel profile number listed in "selection profiles.xls"
    beam_sol = data.iloc[:, 1]

    # Concrete volume to fill voids per beam meter  [m^3/m]
    beam_vol_betonremplissage = data.iloc[:, 14]

    # Welding distance per beam meter [m/m]
    beam_welding = data.iloc[:, 13]

    # Distance between pieces - [mm]
    beam_largeurentrepiece = data.iloc[:, 15]

    # Caoutchouc width per steel profile [mm]
    beam_caoutchoucwidth = data.iloc[:, 18]

    # Steel support place for steel profile width smaller than 200 mm [kN/m]
    supportingplates_mass = data.iloc[:, 11] * 10**-3

    beam_selfweight = None
    profile_unwelding = None
    profile_sandblastedsurf = None

    if steelprofile_type == 1:  # newsteel
        profile_unwelding = data.iloc[:, 16]  # [m/profile] unwelding distance for steel profile deconstruction = 0
        profile_sandblastedsurf = data.iloc[:, 17]  # [m2/m] sandblasting surface for steel profile per meter = 0

    if steelprofile_type == 2:  # reusedsteel
        profile_unwelding = data.iloc[:, 8] # [m/profilé] unwelding distance for reuse steel profile deconstruction
        profile_sandblastedsurf = data.iloc[:, 9]  # [m2/m] ssandblasting surface for reuse steel profile per meter

    if beamposition == 1:   # 1 means below concrete
        beam_selfweight = 1.03  # additional weight factor

    if beamposition == 2:  # 2 means concrete plane
        beam_selfweight = 1.1  # additional weight factor

    profile_MRd = 0.7 * profile_W * fyd / 10**6   # Steel profile bending resistance MRd kNm

    # Return the calculated profile properties
    return (
        profile_mass,
        profile_W,
        profile_I,
        profile_hauteur,
        profile_largeurtot,
        profile_degreasedsurf,
        beam_sol,
        beam_vol_betonremplissage,
        beam_welding,
        beam_largeurentrepiece,
        beam_caoutchoucwidth,
        supportingplates_mass,
        beam_selfweight,
        profile_unwelding,
        profile_sandblastedsurf,
        profile_MRd,
        beam_name,
    )


def cutting_schema(Gslab0: float, v: object, q0: float, q1: float, hsreuse: float, Fsd_armamin: float) -> tuple:
    """Define the cutting scheme
    must ensure that  Mrd_min_reinforcement_0 > Med_1
    Indice 0 are for the donor element and indice 1 is for the new structure
    Parameters
    ----------
    Gslab0 : float
        dead loads [kN/m2]
    v : object
        Variables object.
    q0 : float
         Donor-structure live load
    q1 : float
        New-design live load
    hsreuse : float
        reused-concrete element depth
    Fsd_armamin : float
        Rebar yield strength based on tab. 8 SIA 269.2 [kN/m2]

    Returns
    -------
    tuple
        alpha : float
            maximum ratio between donor span and new span that can be cut
        r_barremin : float
            rebar minimum radius
        Qtotsurfacique1 : float
            total distributed load on new structure

    """

    # Calculate Qtotsurfacique1 - total distributed load on new structure (indice 1) [kN/m^2]
    Qtotsurfacique1 = v.y_Gslab1 * Gslab0 + v.y_rev1 * v.Grev1 + v.y_Q1 * q1

    # Calculate Qtotsurfacique0 - total distributed load on donor structure (indice 0) [kN/m^2]
    Qtotsurfacique0 = v.y_Gslab0 * Gslab0 + v.y_rev0 * v.Grev0 + v.y_Q0 * q0

    # Calculate alpha
    alpha = (Qtotsurfacique0 / Qtotsurfacique1 / 3) ** (1 / 2)

    # Calculate r_barremin - minimum rebar radius based on the donor slab depth [m]
    if hsreuse < 0.18:
        r_barremin = 4 / 1000
    else:
        r_barremin = 5 / 1000

    # Calculate Aire_barremin -rebar minimum area [m^2]
    Aire_barremin = math.pi * r_barremin**2

    # Calculate espa_barremin - minimum spacing between rebars (hypothesis) [m]
    espa_barremin = 0.150

    # Calculate n_barremin - rebar number per meter [n/m]
    n_barremin = 1 / espa_barremin

    # Calculate Aire_armamin - arebar area per meter [m^2]
    Aire_armamin = Aire_barremin * n_barremin

    # Calculate Mrd_armamin - Minimum bending resistance of donor slab [kNm]
    Mrd_armamin = Aire_armamin * Fsd_armamin * 0.81 * hsreuse

    # Calculate L_armamin
    L_armamin = (Mrd_armamin * 8 / Qtotsurfacique1) ** (1 / 2) + 0.15

    return alpha, L_armamin, Qtotsurfacique1


def calculate_LCA_data(v: object, l0: float, alpha: float) -> tuple:
    """Calculate the LCA data

    Parameters
    ----------
    v : object
         Variables object
    l0 : float
        Donor span
    alpha : float
        maximum ratio between donor span and new span that can be cut
    Returns
    -------
    tuple
        _description_
    """
    # Calulate impact lifting with crane
    energrue_levage1kg1m = (
        v.ener_levage1kg1m / v.efficacitegrue
    )  # Energy needed for a crane to lift up 1 kg of 1m [J/m/kg]
    energrue_levage1kg = (
        energrue_levage1kg1m * v.hlevage / 1000000
    )  # Energy used to lift up 1 kg (include conversion J to MJ) [MJ/kg]
    # Calculate impact sawing
    kgco2_prodetelimi_disque = (
        v.vol_1disque * v.massevol_metal * v.kgco2_prodetelimi_acier
    ) / v.surfsciable_1disque  # kgco2/m2 from disc wear
    kgco2_prodetelimi_machine = (
        v.masse_1machine * v.kgco2_prod_machine * (1 + v.facteur_elimi_machine)
    ) / v.surfsciable_1machine  # kgco2/m2 from machine wear

    # impacts unitary carbon
    kgco2_levage = (
        energrue_levage1kg * v.kgco2_energiegrue
    )  # kgCO2/kg of material lift up (crane wear is neglected )
    kgco2_sciage_beton = (
        kgco2_prodetelimi_disque + kgco2_prodetelimi_machine + v.kgco2_prodenergie_sciage
    )  # kgCO2/m2 for concrete sawing

    L_alpha = l0 * alpha

    return L_alpha, kgco2_levage, kgco2_sciage_beton


def calculate_masses(v: object) -> tuple:
    """Calculate the element weights

    Parameters
    ----------
    v : object
        _description_

    Returns
    -------
    tuple
        _description_
    """
    massesurf_panneaux = v.massevol_panneaux * v.h_panneaux  # [kg/m2] weights of horizontal support formwork
    masselin_coffbord = (
        v.h_coffbord * v.h_panneaux * v.n_coffbord * v.massevol_panneaux
    )  # [kg/m] weights of side support formwork
    quantite_poutrelles = 1 / 0.75 + 1 / 2.5  # [m/m2] quantity of temporary beam supports per m2 of formwork
    massesurf_poutrelles = v.masseline_1poutrelle * quantite_poutrelles  # [kg/m2] weights of temporary beam supports per m2 of formwork
    masse_lin_etais = v.poidsunit_etai / v.portee_etai  # shore weight [kg/m2]
    masse_lin_etais_reuse = v.poidsunit_etai / v.portee_etai_reuse  # shore weight for reuse [kg/m2]

    return massesurf_panneaux, masselin_coffbord, massesurf_poutrelles, masse_lin_etais, masse_lin_etais_reuse


def calculate_impact_system_0(
    v, l1, massesurf_panneaux, masselin_coffbord, massesurf_poutrelles, masse_lin_etais, kgco2_levage
):
    """Calculate the LCA of the new slab (System 0)

    Parameters
    ----------
    v : _type_
        _description_
    l1 : float
        new structure span
    massesurf_panneaux : float
        _surface weight of formwork
    masselin_coffbord : float
        _linear weight of side formwork
    massesurf_poutrelles : float
        _surface wieght of temporary beam supports
    masse_lin_etais : float
        _ linear weight of steel shores
    kgco2_levage : float
        _impact lifting

    Returns
    -------
    _type_
        _description_
    """
    if l1 < 4:
        hsnew = 0.18  # hauteur de la dalle neuve [m]
    elif l1 < 6.5:
        hsnew = 0.20  # hauteur de la dalle neuve [m]
    else:
        hsnew = 0.22  # hauteur de la dalle neuve [m]

    volbeton = l1 * hsnew * (1 - v.tauxarmature_neuf)  # [m3/m]

    massebeton = volbeton * v.massevol_beton  # [kg/m]
    volarmature = l1 * hsnew * v.tauxarmature_neuf  # [m3/m]
    massearmature = volarmature * v.massevol_armature  # [kg/m]

    masse_panneaux = l1 * massesurf_panneaux + masselin_coffbord  # [kg/m]
    impact_prod_coffr_new0 = v.kgco2_prod_panneauxcoffrage * masse_panneaux / v.n_uti_panneaux  # [kgco2/m2]

    masse_poutrelles = l1 * massesurf_poutrelles  # [kg/m] quantité de poutrelles sous étais
    masse_etais = l1 * masse_lin_etais  # [kg/m] quantité d'étais
    impact_tp_coffrageetayage_new0 = (
        v.kgco2_tp_camion3240t
        * v.tpdist_coffrageetayage
        * (
            masse_panneaux / v.n_uti_chantier_panneaux
            + masse_poutrelles / v.n_uti_chantier_poutrelles
            + masse_etais / v.n_uti_chantier_etais
        )
        / 1000
    )  # [kgco2/m2]

    impact_levageetdepose_coffrageetayage_new0 = kgco2_levage * (
        masse_panneaux / v.n_uti_chantier_panneaux
        + masse_poutrelles / v.n_uti_chantier_poutrelles
        + masse_etais / v.n_uti_chantier_etais
    )  # [kgco2/m]

    impact_prod_betonneuf_new0 = v.kgco2_prod_beton * massebeton  # [kgco2/m]
    impact_tp_betonneuf_new0 = v.kgco2_tp_camion3240t * massebeton / 1000 * v.tpdist_beton  # [kgco2/m]

    impact_prod_armaneuf_new0 = v.kgco2_prod_armature * massearmature  # [kgco2/m]
    impact_tp_armaneuf_new0 = v.kgco2_tp_camion3240t * v.tpdist_arma * massearmature / 1000  # [kgco2/m]

    impact_levage_armaneuf_new0 = kgco2_levage * massearmature  # [kgco2/m]
    impact_levage_betonneuf_new0 = kgco2_levage * massebeton  # [kgco2/m]

    impact_coulage_betonneuf_new0 = v.kgco2_coulage_beton * volbeton  # [kgco2/m]

    dict_impact_new0 = {}
    dict_impact_new0["prod_coffr"] = impact_prod_coffr_new0
    dict_impact_new0["tp_coffrageetayage"] = impact_tp_coffrageetayage_new0
    dict_impact_new0["levageetdepose_coffrageetayage"] = impact_levageetdepose_coffrageetayage_new0
    dict_impact_new0["prod_betonneuf"] = impact_prod_betonneuf_new0
    dict_impact_new0["tp_betonneuf"] = impact_tp_betonneuf_new0
    dict_impact_new0["prod_armaneuf"] = impact_prod_armaneuf_new0
    dict_impact_new0["tp_armaneuf"] = impact_tp_armaneuf_new0
    dict_impact_new0["levage_armaneuf"] = impact_levage_armaneuf_new0
    dict_impact_new0["levage_betonneuf"] = impact_levage_betonneuf_new0
    dict_impact_new0["coulage_betonneuf"] = impact_coulage_betonneuf_new0

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

    return (impactnew_prod, dict_impact_new0)


def calculate_impact_system_1(
    v,
    masse_lin_etais_reuse,
    kgco2_levage,
    kgco2_sciage_beton,
    dict_impact_new0,
    impactnew_prod,
    l1,
    hsreuse,
    tpdist_beton_reuse,
):
    """Calculate the impact system 1 (reuse of the slab with no cut)

    Parameters
    ----------
    v : _type_
        _description_
    masse_lin_etais_reuse : _type_
        Linear weight of steel shores
    kgco2_levage : _type_
        environmental impacts of lifting
    kgco2_sciage_beton : _type_
        environmental impacts of concrete sawing

    Returns
    -------
    _type_
        _description_

    Raises
    ------
    ValueError
        _description_
    """
    # IMPACT SYSTEM 1 - only simply-supported slabs d (zone 1 and 3)

    # quantity of reused concrete
    masselin_beton_reuse1 = l1 * hsreuse * v.massevol_BA  # reinforced-concrete weigth of the reused slab per meter [kg/m]

    # environmental impact of transport of steel shores
    # quanitiy of steel shores for donor structure per linear meter of the new structure [kg/m] 
    masse_etais_reuse1 = (
        masse_lin_etais_reuse * l1
    )
    impact_tp_etai_reuse1 = masse_etais_reuse1 / 1000 * v.tpdist_coffrageetayage * v.kgco2_tp_camion3240t  # [kgco2/m]

    # env. impact of lifting reused-concrete element and placing on the shores [kgco2/m]
    impact_levageeetdepose_etais_reuse1 = kgco2_levage * 2 * masse_etais_reuse1

    # env. impact of concrete sawing
    # number of concrete element per linear meter [n/m]
    n_bloc_reuse1 = 1 / v.largcamion
    # surface of concrete sawing per linear meter [m2/m]
    surfsciage_reuse1 = ((n_bloc_reuse1 * l1) + 1) * 2 * hsreuse
   
    # neglect that one linear cut could potentially be used in two reused-concrete elements # [kgco2/m]
    impact_sciage_betonreused_reuse1 = kgco2_sciage_beton * surfsciage_reuse1

    # env. impact of removing (lifting) reused-concrete elements from donor structure [kgco2/m]
    impact_depose_betonreused_reuse1 = kgco2_levage * masselin_beton_reuse1

    # env. impact of transportation of reused-concrete elements [kgco2/m]
    impact_tp_betonreused_reuse1 = (
        masselin_beton_reuse1 / 1000 * tpdist_beton_reuse * v.kgco2_tp_camion3240t
    )

    # env. impact of the production of the steel corners
    if hsreuse == 0.14:
        epaisseurcorn = 0.013  #  thickness of the steel corners LNP (from SZS table)
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
    else:
        raise ValueError("hsreuse doit être 0.14, 0.16, 0.18, 0.20 ou 0.22")

    # Volume of steel corners per meter [m3/m/corner]
    volcormetal = hcorn * 2 * epaisseurcorn
    # par corner [m3/m/corner]
    n_cor = 2
    # corner length per linear meter of support (hypothesis) [m cornière /m]
    qcorniere = 0.4 

    # Volumer of steel corners per linear meter [m3/m]
    voltotcormetal = volcormetal * n_cor * qcorniere
    # linear weight of steel corners per meter [kg/m]
    massemetalcorn_reuse1 = voltotcormetal * v.massevol_metal

    # env. impact of the production of steel corner
    impact_prod_metalneuf_corn_reuse1 = massemetalcorn_reuse1 * v.kgco2_prod_profilmetal

    
    # New steel plates and bolts [m3/plaque]
    vol_1plaque = 0.25 * 0.15 * 0.008 + 3.14 * 0.008**2 * hsreuse * 4
    
    # number of plates (hypothesis plates every 1.5 meters over the span and min two plates)[plate/m]
    n_plaque_reuse1 = (2 + math.ceil(l1 / 2)) / v.largcamion  # nombre de plaque par mètre linéaire [plaque/m]
    
    # linear weigth of steel plates[kg/m]
    massemetalplaque_reuse1 = (
        vol_1plaque * n_plaque_reuse1 * v.massevol_metal
    ) 
    # env. impact of steel plate production [kgco2/m]
    impact_prod_metalneuf_plaque_reuse1 = massemetalplaque_reuse1 * v.kgco2_prod_profilmetal

    # env. impact of transportation of steel corners [kgco2/m]
    impact_tp_metalneuf_corn_reuse1 = (
        massemetalcorn_reuse1 / 1000 * v.tpdist_metal * v.kgco2_tp_camion3240t
    )

    #  env. impact of transportation of steel plates [kgco2/m]
    impact_tp_metalneuf_plaque_reuse1 = (
        massemetalplaque_reuse1 / 1000 * v.tpdist_metal * v.kgco2_tp_camion3240t
    )

    # env. impact of protective painting [kgco2/m]
    # surface to paint per meter of corners [m2/m]
    surfacepeintparcorn = hcorn
    surfacepeinttot_reuse1 = (
        surfacepeintparcorn * n_cor * qcorniere
    )
     # env. impact of protective painting production [kgco2/m]
    impact_prod_revpulvacier_reuse1 = v.kgco2_prod_revpulvacier * surfacepeinttot_reuse1

    # impact de la production du caoutchouc
    
    surfacecaoutchoucparcorn = (
        hcorn
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

    # impact du levage  du béton
    impact_levage_betonreused_reuse1 = kgco2_levage * masselin_beton_reuse1  # [kgco2/m]

    # impact du joint
    volumejointpoly = 0.02 * 0.02 * l1 / v.largcamion  # [m3/m]
    impact_prod_jointpolyneuf_reuse1 = v.kgco2_prod_jointpoly * v.massevol_jointpoly * volumejointpoly  # [kgco2/m]

    # impact du mortier dans les joints entre les pieces de beton
    volumemortier = (hsreuse - 0.03) * 0.02 * l1 / v.largcamion  # [m3/m]
    impact_prod_mortierneuf_reuse1 = volumemortier * v.massevol_mortier * v.kgco2_prod_mortier  # [kgco2/m]

    # impact EVITE de l'élimination du béton réutilisé
    impact_EVITE_elimi_betonreused_reuse1 = v.kgco2_elimi_beton * masselin_beton_reuse1  # [kgco2/m]

    # impact EVITE de l'élimination de l'acier d'armature réutilisé
    volarma0 = l1 * hsreuse * v.tauxarmature0  # volume des armatures réutilisées  [m3/m]
    massearma0 = v.massevol_armature * volarma0  # masse des armatures réutilisées [m3/m]
    impact_EVITE_elimi_armareused_reuse1 = v.kgco2_elimi_armature * massearma0  # [kgco2/m]

    impact_levageetdepose_coffrageetetayage_new0 = 0  # to change !!!!!!

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
        impact_prod_revpulvacier_reuse1,
        impact_prod_jointpolyneuf_reuse1,
        +impact_prod_caoutchouc_reuse1,
        impact_prod_mortierneuf_reuse1,
        impact_prod_metalneuf_corn_reuse1,
        impact_prod_metalneuf_plaque_reuse1,
        impact_sciage_betonreused_reuse1,
        impact_tp_betonreused_reuse1,
        impact_tp_etai_reuse1
        + impact_levageeetdepose_etais_reuse1
        + impact_depose_betonreused_reuse1
        + impact_levage_betonreused_reuse1
        + impact_tp_metalneuf_corn_reuse1
        + impact_tp_metalneuf_plaque_reuse1
        + impact_degraissage_metalneuf_reuse1
        + impact_levage_metalneuf_plaque_reuse1
        + impact_levage_metalneuf_corn_reuse1,
    ]

    impactnew1_matrice = [
        dict_impact_new0.get("tp_armaneuf")
        + dict_impact_new0.get("levage_armaneuf")
        + dict_impact_new0.get("levage_betonneuf")
        + dict_impact_new0.get("coulage_betonneuf")
        + dict_impact_new0.get("prod_coffr")
        + dict_impact_new0.get("tp_coffrageetayage")
        + dict_impact_new0.get("tp_coffrageetayage")
        + impact_levageetdepose_coffrageetetayage_new0
        + impact_EVITE_elimi_armareused_reuse1,
        dict_impact_new0.get("prod_armaneuf"),
        dict_impact_new0.get("prod_betonneuf"),
        dict_impact_new0.get("tp_betonneuf"),
        impact_EVITE_elimi_betonreused_reuse1,
    ]

    # impact neuf
    impactnew = impactnew_prod + impact_EVITE_elimi_betonreused_reuse1 + impact_EVITE_elimi_armareused_reuse1

    number_of_slab = 1

    return impactreuse1, impactreuse1_matrice, impactnew1_matrice, impactnew, number_of_slab


def calculate_impact_system_2(
    v,
    l1,
    l0,
    q1,
    hsreuse,
    tpdist_beton_reuse,
    tpdist_metal_reuse,
    L_armamin,
    L_alpha,
    beamposition,
    Qtotsurfacique1,
    beam_selfweight,
    profile_MRd,
    profile_I,
    beam_largeurentrepiece,
    Ibeton,
    steelprofile_type,
    Gslab0,
    profile_W,
    profile_mass,
    profile_largeurtot,
    profile_hauteur,
    profile_degreasedsurf,
    beam_welding,
    profile_unwelding,
    profile_sandblastedsurf,
    beam_vol_betonremplissage,
    beam_caoutchoucwidth,
    beam_sol,
    supportingplates_mass,
    masse_lin_etais_reuse,
    kgco2_levage,
    kgco2_sciage_beton,
    impactnew_prod,
    dict_impact_new0,
    beam_name,
):
    L_decoupeL0 = None

    if l0 <= L_armamin and l1 > l0:  # conditions de la zone 2
        L_decoupeL0 = l0
    elif (
        l1 > l0 and l0 > L_armamin or l1 <= l0 and l1 > L_alpha and l1 > L_armamin
    ):  # conditions de la zone 4 et de la zone 5
        L_decoupeL0 = max(L_alpha, L_armamin)

    if beamposition == 1:  # belowconcrete
        pass

    Qlin = L_decoupeL0 * Qtotsurfacique1 * beam_selfweight  # [kN/m]

    # SELECTION PROFILE - SELECTIONS CARACT. A COMPLETER
    Med = Qlin * (l1**2) / 8  # Nmm
    ind = np.where(profile_MRd > Med)[0]

    Selection_I = profile_I[np.min(ind)]
    Selection_beam_largeurentrepiece = beam_largeurentrepiece[np.min(ind)]

    it = 0
    flechemax_freq = l1 * 1000 / 350  # mm
    flechemax_perm = l1 * 1000 / 300  # mm
    sel = np.min(ind)

    while True:
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
            condition_1 = True
        else:
            condition_1 = False
            it += 1
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
                condition_2 = True
            else:
                condition_2 = False
                it += 1
                sel = np.min(ind) + it
                Selection_I = profile_I[sel]
                Selection_beam_largeurentrepiece = beam_largeurentrepiece[sel]
        else:
            condition_2 = True

        # Exit the loop if both conditions are true
        if condition_1 and condition_2:
            break

    beam_name_text = beam_name[sel]
    profile_W[sel]
    Selection_I = profile_I[sel]
    Selection_profile_mass = profile_mass[sel]
    Selection_profile_hauteur = profile_hauteur[sel]
    Selection_profile_largeurtot = profile_largeurtot[sel]
    Selection_profile_degreasedsurf = profile_degreasedsurf[sel]
    beam_sol[sel]
    Selection_beam_welding = beam_welding[sel]
    supportingplates_mass[sel]
    Selection_profile_unwelding = profile_unwelding[sel]
    Selection_profile_sandblastedsurf = profile_sandblastedsurf[sel]
    Selection_beam_largeurentrepiece = beam_largeurentrepiece[sel]
    Selection_beam_vol_betonremplissage = beam_vol_betonremplissage[sel]
    Selection_beam_caoutchoucwidth = beam_caoutchoucwidth[sel]

    # IMPACTS COMMUNS À TOUS LES SYSTÈMES 2
    # Ratio dalle:poutre
    if beamposition == 1:  # belowconcrete
        qdalle = 1
    elif beamposition == 2:  # concrete plane
        qdalle = 1 / (L_decoupeL0 + Selection_beam_largeurentrepiece / 1000) * L_decoupeL0

    # Quantité de métal pour les plaques métalliques
    vol_1plaque = 0.2 * 0.15 * 0.01 + 3.14 * 0.008**2 * hsreuse * 4  # Volume par plaque avec boulons [m3/plaque]
    n_plaque_reuse2 = (
        (2 * np.ceil(l1 / v.largcamion) + np.ceil(L_decoupeL0 / 1.5)) / L_decoupeL0 * qdalle
    )  # Nombre de plaque par mètre linéaire [plaque/m]
    massemetalplaque_reuse2 = (
        vol_1plaque * n_plaque_reuse2 * v.massevol_metal
    )  # Masse linéaire de métal pour les plaques [kg/m]

    # Surface de béton sciée
    n_bloc_reuse2 = np.ceil(l1 / v.largcamion)  # Nombre de blocs nécessaires pour couvrir L1
    surfsciage_reuse2 = (
        (l1 / L_decoupeL0 * 2 + (n_bloc_reuse2 * 2)) * hsreuse * qdalle
    )  # Surface de béton sciée par mètre linéaire [m2/m]

    # Impact du transport des étais pour le donneur
    masse_etais_reuse2 = (
        masse_lin_etais_reuse * l1 * qdalle
    )  # Quantité étais pour découpe donneur par mètre linéaire receveur
    impact_tp_etais_reuse2 = masse_etais_reuse2 / 1000 * v.tpdist_coffrageetayage * v.kgco2_tp_camion3240t  # [kgco2/m]

    # Impact du levage et de la dépose des étais
    impact_levageetdepose_etais_reuse2 = kgco2_levage * masse_etais_reuse2  # [kgco2/m]

    # Impact du sciage du béton
    impact_sciage_betonreused_reuse2 = kgco2_sciage_beton * surfsciage_reuse2  # [kgco2/m]

    # Impact du joint entre les pièces de béton
    volumejointpoly2 = 0.02 * 0.02 * n_bloc_reuse2  # [m3/m]
    impact_prod_jointpolyneuf_reuse2 = (
        v.kgco2_prod_jointpoly * v.massevol_jointpoly * volumejointpoly2 * qdalle
    )  # [kgco2/m]

    # Impact du mortier dans les joints entre les pièces de béton
    volumemortier2 = (hsreuse - 0.03) * 0.02 * n_bloc_reuse2  # [m3/m]
    impact_prod_mortierneuf_reuse2 = volumemortier2 * v.massevol_mortier * v.kgco2_prod_mortier * qdalle  # [kgco2/m]

    # Quantité de métal pour les poutres
    qpoutreparmlin = 1 / (
        L_decoupeL0 + (Selection_beam_largeurentrepiece / 1000)
    )  # Nombre moyen de poutre par mètre (de large) de plancher
    masselin_poutre = (
        qpoutreparmlin * Selection_profile_mass * 100 * l1
    )  # Masse de métal moyenne par mètre linéaire de plancher [kg/m] !! ATTENTION À LA CONVERSION

    # Quantité de béton de réemploi
    lbetonparmlin = 1 - (
        (Selection_beam_largeurentrepiece / 1000) * qpoutreparmlin
    )  # Longueur de béton par m linéaire [m/m] À VÉRIFIER
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
    impact_tp_metalneuf_plaque_reuse2 = massemetalplaque_reuse2 / 1000 * v.tpdist_metal * v.kgco2_tp_camion3240t

    # Impact du transport des cornières métalliques
    impact_tp_metalneuf_corn_reuse2 = masse_corn2 / 1000 * v.tpdist_metal * v.kgco2_tp_camion3240t

    # Impact des soudures sur l'acier
    impact_welding_reuse2 = Selection_beam_welding * l1 * qpoutreparmlin * v.kgco2_welding

    # Impact du dégraissage de l'acier
    surface_peint_1beam = Selection_profile_degreasedsurf  # Facteur 1/1000 enlevé
    surfacepeinttot_reuse2 = (
        surface_peint_1beam * qpoutreparmlin * l1
    )  # Surface à protéger avec peinture ignifuge par mètre linéaire de plancher [m2/m]
    impact_degraissage_metalneuf_reuse2 = v.kgco2_degraissage * surfacepeinttot_reuse2

    # Impact de la production de la peinture protectrice
    impact_prod_revpulvacier_reuse2 = v.kgco2_prod_revpulvacier * surfacepeinttot_reuse2

    # Impact de la production du caoutchouc
    volumecaoutchouctot_reuse2 = (
        Selection_beam_caoutchoucwidth / 1000 * l1 * qpoutreparmlin * v.epaisseur_caoutchouc
    )  # Volume de caoutchouc par mètre linéaire de plancher [m3/m]
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
    massearma0 = v.massevol_armature * volarma0  # Masse des armatures réutilisées [m3/m]
    impact_EVITE_elimi_armareused_reuse2 = v.kgco2_elimi_armature * massearma0  # [kgco2/m]

    # IMPACTS SPECIAUX POUR SYSTEMES 2 AVEC PROFILES NEUFS
    if steelprofile_type == 1:  # recycledsteel
        # Impact de la production des profilés métalliques
        impact_prod_metalneuf_profiles_reuse2 = masselin_poutre * v.kgco2_prod_profilmetal

        # Impact du transport des profilés métalliques
        impact_tp_metalneuf_profiles_reuse2 = masselin_poutre / 1000 * v.tpdist_metal * v.kgco2_tp_camion3240t

        # Impact du levage des profillés métalliques
        impact_levage_metalneuf_profiles_reuse2 = kgco2_levage * masselin_poutre  # [kgco2/m]

    if steelprofile_type == 2:  # reusedsteel
        impact_prod_metalneuf_profiles_reuse2 = 0
        impact_tp_metalneuf_profiles_reuse2 = 0
        impact_levage_metalneuf_profiles_reuse2 = 0

    # IMPACTS SPECIAUX POUR SYSTEMES 2 AVEC PROFILES REEMPLOI
    if steelprofile_type == 1:  # recycledsteel
        impact_unwelding_metalreuse_reuse2 = 0
        impact_depose_metalreused_reuse2 = 0
        impact_sablage_metalreused_reuse2 = 0
        impact_tp_metalreused_reuse2 = 0
        impact_EVITE_elimi_metalreused_reuse2 = 0

    if steelprofile_type == 2:  # reusedsteel
        # Impact de l'ouverture/unwelding connections sur le donneur
        impact_unwelding_metalreuse_reuse2 = Selection_profile_unwelding * qpoutreparmlin * v.kgco2_welding  # [kgco2/m]

        # Impact de la dépose des profilés de réemploi
        impact_depose_metalreused_reuse2 = kgco2_levage * masselin_poutre  # [kgco2/m]

        # Impact du sablage des profilés
        impact_sablage_metalreused_reuse2 = (
            Selection_profile_sandblastedsurf * l1 * qpoutreparmlin * v.kgco2_sandblasting
        )  # [kgco2/m]

        # Impact du transport des profilés de réemploi
        impact_tp_metalreused_reuse2 = masselin_poutre / 1000 * tpdist_metal_reuse * v.kgco2_tp_camion3240t  # [kgco2/m]

        # Impact EVITE de l'élimination des profilés métalliques réutilisés
        impact_EVITE_elimi_metalreused_reuse2 = masselin_poutre * v.kgco2_elimi_profilmetal  # [kgco2/m]

    # IMPACTS SPECIAUX POUR SYSTEMS 2 AVEC PROFILES DANS LE PLAN DU BETON
    # -> RAJOUTER LA PROD ET LE TP DU BETON DANS LES PROFILES!
    if beamposition == 1:  # belowconcrete
        impact_prod_betonnew_reuse2 = 0
        impact_tp_betonnew_reuse2 = 0

    if beamposition == 2:  # concreteplan
        if Selection_profile_hauteur / 1000 <= hsreuse:
            pass
        if Selection_profile_hauteur / 1000 > hsreuse:
            pass
        masse_betonremplissage_tot = (
            (Selection_beam_vol_betonremplissage + v.masse_betonremplissage_complement)
            * qpoutreparmlin
            * v.massevol_beton
            * l1
        )  # [m3/m de poutre]*[kg/m3]*[qpoutre/m]
        impact_prod_betonnew_reuse2 = masse_betonremplissage_tot * v.kgco2_prod_beton
        impact_tp_betonnew_reuse2 = masse_betonremplissage_tot / 1000 * v.kgco2_tp_camion3240t * v.tpdist_beton

    # impact réemploi
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

    # impact neuf
    impactnew = (
        impactnew_prod
        + impact_EVITE_elimi_betonreused_reuse2
        + impact_EVITE_elimi_armareused_reuse2
        + impact_EVITE_elimi_metalreused_reuse2
    )

    # distribution des impacts (réemploi et new)
    impactreuse2_matrice = [
        impact_prod_revpulvacier_reuse2,
        impact_prod_jointpolyneuf_reuse2,
        impact_prod_caoutchouc_reuse2,
        impact_prod_mortierneuf_reuse2,
        impact_prod_metalneuf_corn_reuse2,
        impact_prod_metalneuf_plaque_reuse2,
        impact_prod_metalneuf_profiles_reuse2,
        impact_sciage_betonreused_reuse2,
        impact_tp_betonreused_reuse2,
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
    ]

    impactnew2_matrice = [
        impact_EVITE_elimi_armareused_reuse2
        + impact_EVITE_elimi_metalreused_reuse2
        + dict_impact_new0.get("prod_coffr")
        + dict_impact_new0.get("tp_coffrageetayage")
        + dict_impact_new0.get("levageetdepose_coffrageetayage")
        + dict_impact_new0.get("tp_armaneuf")
        + dict_impact_new0.get("levage_armaneuf")
        + dict_impact_new0.get("levage_betonneuf")
        + dict_impact_new0.get("coulage_betonneuf"),
        dict_impact_new0.get("prod_armaneuf"),
        dict_impact_new0.get("prod_betonneuf"),
        dict_impact_new0.get("tp_betonneuf"),
        impact_EVITE_elimi_betonreused_reuse2,
    ]

    number_of_slab = 1

    return impactreuse2, impactreuse2_matrice, impactnew2_matrice, impactnew, number_of_slab, beam_name_text


def create_df_chart(values: list, labels: list):
    bar_char_data = pd.DataFrame({"labels": labels, "values": values})
    bar_char_data.set_index("labels", inplace=True)
    return bar_char_data


def processing(
    l0: float,
    l1: float,
    hsreuse=float,
    year=int,
    q0=int,
    q1=int,
    tpdist_beton_reuse=float,
    tpdist_metal_reuse=float,
    steelprofile_type=int,
):
    # retrive variables from yaml file
    with open(VARIABLES_FILE_PATH) as file:
        variables = yaml.safe_load(file)
    v = MyConfig(variables)

    # --------------------------------------------------------
    # caractérstiques du donneur
    Fsd_armamin = define_fsd_armamin(year)
    beamposition = 1

    # charge permanentes [kN/m2]
    Gslab0 = hsreuse * v.massevol_BA / 100

    # Inertie section par metre [mm4]
    Ibeton = ((hsreuse * 1000) ** 3) * 1000 / 12

    # --------------------------------------------------------
    # caractérstiques du receveur
    fyd = define_fyd(steelprofile_type=steelprofile_type)

    # données sur les profilés pour système 2
    (
        profile_mass,
        profile_W,
        profile_I,
        profile_hauteur,
        profile_largeurtot,
        profile_degreasedsurf,
        beam_sol,
        beam_vol_betonremplissage,
        beam_welding,
        beam_largeurentrepiece,
        beam_caoutchoucwidth,
        supportingplates_mass,
        beam_selfweight,
        profile_unwelding,
        profile_sandblastedsurf,
        profile_MRd,
        beam_name,
    ) = get_profile_data(steelprofile_type=steelprofile_type, beamposition=beamposition, fyd=fyd)

    # schéma de découpes
    alpha, L_armamin, Qtotsurfacique1 = cutting_schema(Gslab0, v, q0, q1, hsreuse, Fsd_armamin)

    # données coffrage et étayage pour NEW (SYSTEM 0)
    # panneaux
    (
        massesurf_panneaux,
        masselin_coffbord,
        massesurf_poutrelles,
        masse_lin_etais,
        masse_lin_etais_reuse,
    ) = calculate_masses(v)

    # données LCA
    # distances
    L_alpha, kgco2_levage, kgco2_sciage_beton = calculate_LCA_data(v, l0, alpha)

    # Impact new (SYSTEM 0)
    (impactnew_prod, dict_impact_new0) = calculate_impact_system_0(
        v, l1, massesurf_panneaux, masselin_coffbord, massesurf_poutrelles, masse_lin_etais, kgco2_levage
    )

    if l1 <= L_armamin and l1 <= l0 or l1 <= L_alpha and l1 > L_armamin:  # conditions de la zone 1 et de la zone 3
        system_id = 1
        system_text = "Cut concrete as primary elements"
        # Impact reuse (SYSTEM 1)
        impactreuse, impactreuse_matrice, impactnew_matrice, impactnew, number_of_slab = calculate_impact_system_1(
            v,
            masse_lin_etais_reuse,
            kgco2_levage,
            kgco2_sciage_beton,
            dict_impact_new0,
            impactnew_prod,
            l1,
            hsreuse,
            tpdist_beton_reuse,
        )

    else:
        # Impact reuse (SYSTEM 2)
        (
            impactreuse,
            impactreuse_matrice,
            impactnew_matrice,
            impactnew,
            number_of_slab,
            beam_name_text,
        ) = calculate_impact_system_2(
            v,
            l1,
            l0,
            q1,
            hsreuse,
            tpdist_beton_reuse,
            tpdist_metal_reuse,
            L_armamin,
            L_alpha,
            beamposition,
            Qtotsurfacique1,
            beam_selfweight,
            profile_MRd,
            profile_I,
            beam_largeurentrepiece,
            Ibeton,
            steelprofile_type,
            Gslab0,
            profile_W,
            profile_mass,
            profile_largeurtot,
            profile_hauteur,
            profile_degreasedsurf,
            beam_welding,
            profile_unwelding,
            profile_sandblastedsurf,
            beam_vol_betonremplissage,
            beam_caoutchoucwidth,
            beam_sol,
            supportingplates_mass,
            masse_lin_etais_reuse,
            kgco2_levage,
            kgco2_sciage_beton,
            impactnew_prod,
            dict_impact_new0,
            beam_name,
        )
        system_id = 2
        system_text = f"Cut concrete over new {beam_name_text} steel profile"

    drawing_data = {}
    drawing_data["l0"] = l0
    drawing_data["l1"] = l1
    drawing_data["h"] = hsreuse
    drawing_data["number_part"] = number_of_slab  # Where to get this information ?

    df_barchart = create_df_chart(values=[impactnew / l1, impactreuse / l1], labels=["Impact new", "Impact reuse"])

    df_piechart_reuse = create_df_chart(
        values=impactreuse_matrice, labels=[f"label_{i}" for i, v in enumerate(impactreuse_matrice)]
    )
    df_piechart_new = create_df_chart(
        values=impactnew_matrice, labels=[f"label_{i}" for i, v in enumerate(impactnew_matrice)]
    )

    return [system_text, drawing_data, df_barchart, df_piechart_reuse, df_piechart_new, system_id]


if __name__ == "__main__":
    l0 = 3
    l1 = 6
    hsreuse = 0.14
    year = 2
    q0 = 2
    q1 = 2
    tpdist_beton_reuse = 20
    tpdist_metal_reuse = 80
    steelprofile_type = 1

    result = processing(
        l0=l0,
        l1=l1,
        hsreuse=hsreuse,
        year=year,
        q0=q0,
        q1=q1,
        tpdist_beton_reuse=tpdist_beton_reuse,
        tpdist_metal_reuse=tpdist_metal_reuse,
        steelprofile_type=steelprofile_type,
    )

    print(result[0])
