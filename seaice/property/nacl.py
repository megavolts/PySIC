import numpy as np

def sw_c3515():
    # conductivity of sea water at 35 PSU, 15 C and sea level pressure p=0
    # mS/cm
    return 42.914

def sw_salrt(T):
    # conductivity ratio rt(T) = C(35, T, 0)/(35,15,0)
    c0 = 0.6766097;
    c1 = 2.00564e-2;
    c2 = 1.104259e-4;
    c3 = -6.9698e-7;
    c4 = 1.0031e-9;
    rt = c0 + (c1 + (c2 + (c3 + c4 * T) * T) * T) * T;
    return rt

def sw_salrp(R, T, P):
    # equation 4 (p.8) UNESCO
    # Conductivity ratio   Rp(S,T,P) = C(S,T,P)/C(S,T,0)

    d1 = 3.426e-2;
    d2 = 4.464e-4;
    d3 = 4.215e-1;
    d4 = -3.107e-3;

    e1 = 2.070e-5;
    e2 = -6.370e-10;
    e3 = 3.989e-15;

    Rp = 1 + (P*(e1 + e2*P + e3*P**2))/(1 + d1* T + d2* T**2 + (d3 + d4*T)*R)
    return Rp


def sw_sals(Rt, T):
    '''
    Salinity of sea water as function of Rt and T
    UNESCO 1983 polynomial, equation 1, 2 and 7

    References:
       Fofonoff, P. and Millard, R.C. Jr
       Unesco 1983. Algorithms for computation of fundamental properties of
       seawater, 1983. _Unesco Tech. Pap. in Mar. Sci._, No. 44, 53 pp.

    :param Rt: Rt(S, T) = C(S, T, 0)/C(35, T, 0)
    :param T: temperature [degree C]
    :return S: salinity [PSU]
    '''

    a0 = 0.0080
    a1 = -0.1692
    a2 = 25.3851
    a3 = 14.0941
    a4 = -7.0261
    a5 = 2.7081

    b0 = 0.0005
    b1 = -0.0056
    b2 = -0.0066
    b3 = -0.0375
    b4 = 0.0636
    b5 = -0.0144

    k = 0.0162

    Rtx = np.sqrt(Rt)
    del_T = T - 15
    del_S = (del_T / (1 + k * del_T)) * (b0 + (b1 + (b2 + (b3 + (b4 + b5 * Rtx) * Rtx) * Rtx) * Rtx) * Rtx)

    S = a0 + (a1 + (a2 + (a3 + (a4 + a5 * Rtx) * Rtx) * Rtx) * Rtx) * Rtx
    S = S + del_S

    return S


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
