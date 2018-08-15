import numpy as np




def nacl_c3515():
    return nacl_c(sw_c3515())

def nacl_c(c):
    # c mS/cm
    # nacl_c mS/cm
    return c*1.056

def sw_nacl_con2sal_cal(c, T, P=0):
    cndrsw = c/sw_c3515()
    con25 = c/(sw_salrt(T)/sw_salrt(25))

    # polynom p1 valid below 1.2 mS/cm at 25 °C (S~0.6)
    p1 = [-1.247514714105395, 1.888558315644160, 0.476651642658910]

    # polynom p2 valid below above 1.2 mS/cm at 35 (S~0.6)
    p2 = [0.000014549965652, -0.000441051717178, 0.004858369979778, -0.028387627621333, 1.080106358899861]

    crat1 = np.polyval(p1, con25**(1/2))
    crat2 = np.polyval(p2, con25**(1/2))

    crat = crat2
    if crat1[con25 < 0.6].__len__() > 0:
        crat[con25 < 0.6] = crat1[con25 < 0.6]
    if crat[con25 < 0.06].__len__() > 0:
        crat[con25 < 0.06] = np.nan

    cndrna = c * crat / nacl_c3515()
    R = cndrsw
    rt = sw_salrt(T)
    Rp = sw_salrp(R, T, P)
    Rt = R/(Rp * rt)
    Sw = sw_sals(Rt, T)

    Rna = cndrna
    rt = sw_salrt(T)
    Rpna = sw_salrp(Rna, T, P)
    Rtna = Rna/(Rpna * rt)
    Snacl = sw_sals(Rtna, T)

    return Sw, Snacl


def sw_con2sal(c, T, P=0):
    cndrsw = c/sw_c3515()
    con25 = c/(sw_salrt(T)/sw_salrt(25))

    # polynom p1 valid below 1.2 mS/cm at 25 °C (S~0.6)
    p1 = [-1.247514714105395, 1.888558315644160, 0.476651642658910]

    # polynom p2 valid below above 1.2 mS/cm at 35 (S~0.6)
    p2 = [0.000014549965652, -0.000441051717178, 0.004858369979778, -0.028387627621333, 1.080106358899861]

    crat1 = np.polyval(p1, con25**(1/2))
    crat2 = np.polyval(p2, con25**(1/2))

    crat = crat2
    if crat1[con25 < 0.6].__len__() > 0:
        crat[con25 < 0.6] = crat1[con25 < 0.6]
    if crat[con25 < 0.06].__len__() > 0:
        crat[con25 < 0.06] = np.nan

    R = cndrsw
    rt = sw_salrt(T)
    Rp = sw_salrp(R, T, P)
    Rt = R/(Rp * rt)
    Sw = sw_sals(Rt, T)
    return Sw


def snacl_con2sal(c, T, P=0):
    '''
        :param c: conductivity [mS/cm]
        :param T: temperature [degree C]
        :param P: pressure at sea-level
        :return Snacl: salinity of nacl solution in k/kg
    '''

    con25 = c/(sw_salrt(T)/sw_salrt(25))

    # polynom p1 valid below 1.2 mS/cm at 25 °C (S~0.6)
    p1 = [-1.247514714105395, 1.888558315644160, 0.476651642658910]

    # polynom p2 valid below above 1.2 mS/cm at 35 (S~0.6)
    p2 = [0.000014549965652, -0.000441051717178, 0.004858369979778, -0.028387627621333, 1.080106358899861]

    crat1 = np.polyval(p1, con25**(1/2))
    crat2 = np.polyval(p2, con25**(1/2))

    crat = crat2
    if crat1[con25 < 0.6].__len__() > 0:
        crat[con25 < 0.6] = crat1[con25 < 0.6]
    if crat[con25 < 0.06].__len__() > 0:
        crat[con25 < 0.06] = np.nan

    cndrna = c * crat / nacl_c3515()

    Rna = cndrna
    rt = sw_salrt(T)
    Rpna = sw_salrp(Rna, T, P)
    Rtna = Rna/(Rpna * rt)
    Snacl = sw_sals(Rtna, T)

    return Snacl
