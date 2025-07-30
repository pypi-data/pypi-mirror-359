import math
from typing import Sequence, Mapping, Optional, Union

# Pesos de referência do IQA-CETESB (ordem: OD, CF, pH, DBO, NT, FT, Temp, Turbidez, Sólidos)
_DEFAULT_WEIGHTS = {
    "od":   0.17,
    "cf":   0.15,
    "ph":   0.12,
    "dbo":  0.10,
    "nt":   0.10,
    "ft":   0.10,
    "temp": 0.10,
    "tb":   0.08,
    "st":   0.08,
}

def _parse_weights(
    weights: Optional[Union[Sequence[float], Mapping[str, float]]]
) -> Mapping[str, float]:
    """
    Normaliza o argumento ``weights`` para um dicionário com as nove chaves
    padronizadas. Aceita:
      • lista/tupla de 9 valores (na ordem _DEFAULT_WEIGHTS) ou  
      • dict parcial/total com qualquer subconjunto dessas chaves.
    """
    if weights is None:
        return _DEFAULT_WEIGHTS

    if isinstance(weights, Sequence):
        if len(weights) != 9:
            raise ValueError("Se 'weights' for sequência, deve conter 9 valores.")
        return dict(zip(_DEFAULT_WEIGHTS, map(float, weights)))

    if isinstance(weights, Mapping):
        # Preenche ausentes com o padrão; preserva os demais
        final = _DEFAULT_WEIGHTS.copy()
        for k, v in weights.items():
            if k not in _DEFAULT_WEIGHTS:
                raise KeyError(
                    f"Chave de peso desconhecida: '{k}'. "
                    f"Use {list(_DEFAULT_WEIGHTS.keys())}"
                )
            final[k] = float(v)
        return final

    raise TypeError("'weights' deve ser None, sequência ou mapeamento.")


def WQI(*args, **kwargs):
    """Alias internacional para IQA."""
    return IQA(*args, **kwargs)


def IQA(
    oxigenio_dissolvido: float,
    coliformes_fecais: float,
    ph: float,
    dbo: float,
    nitrogenio_total: float,
    fosforo_total: float,
    turbidez: float,
    solidos_totais: float,
    altitude: Optional[float] = None,
    temperatura: Optional[float] = None,
    weights: Optional[Union[Sequence[float], Mapping[str, float]]] = None,
):
    """
    Calcula o Índice de Qualidade da Água (IQA) segundo a metodologia CETESB,
    permitindo ajustar os pesos dos nove parâmetros.

    Parâmetros adicionais
    ---------------------
    weights : list[float] | dict[str,float] | None
        • list/tuple de 9 valores (ordem: OD, CF, pH, DBO, NT, FT, Temp, Turbidez, Sólidos)
        • ou dict com qualquer subconjunto das chaves acima.
        • se None, usa os pesos oficiais.
    """

    # ---------- Preparação ----------
    w = _parse_weights(weights)

    # Altitude e temperatura padrão
    altitude = 200 if altitude is None else altitude
    temperatura = 22 if temperatura is None else temperatura

    # ---------- 1) Oxigênio Dissolvido ----------
    cs = (
        (14.62 - 0.3898 * temperatura + 0.006969 * temperatura**2 - 0.00005896 * temperatura**3)
        * (1 - 0.0000228675 * altitude) ** 5.167
    )
    psat = 100 * oxigenio_dissolvido / cs

    if 0 < psat <= 50:
        q_od = 3 + 0.34 * psat + 0.008095 * psat**2 + 1.35252e-5 * psat**3
    elif psat <= 85:
        q_od = 3 - 1.166 * psat + 0.058 * psat - 3.803435e-5 * psat**3
    elif psat <= 100:
        q_od = 3 + 3.7745 * psat**0.704889
    elif psat <= 140:
        q_od = 3 + 2.9 * psat - 0.02496 * psat**2 + 5.60919e-5 * psat**3
    else:
        q_od = 50  # valor de saturação acima da faixa
    p_od = q_od**w["od"]

    # ---------- 2) Coliformes Fecais ----------
    cf_log = math.log10(coliformes_fecais)
    if 0 < cf_log <= 1:
        q_cf = 100 - 33 * cf_log
    elif cf_log <= 5:
        q_cf = 100 - 37.2 * cf_log + 3.60743 * cf_log**2
    else:
        q_cf = 3
    p_cf = q_cf**w["cf"]

    # ---------- 3) pH ----------
    if 0 < ph <= 2:
        q_ph = 2.0
    elif ph <= 4:
        q_ph = 13.6 - 10.6 * ph + 2.4364 * ph**2
    elif ph <= 6.2:
        q_ph = 155.5 - 77.36 * ph + 10.2481 * ph**2
    elif ph <= 7:
        q_ph = -657.2 + 197.38 * ph - 12.9167 * ph**2
    elif ph <= 8:
        q_ph = -427.8 + 142.05 * ph - 9.695 * ph**2
    elif ph <= 8.5:
        q_ph = 216 - 16 * ph
    elif ph <= 9:
        q_ph = 1_415_823 * math.exp(-1.1507 * ph)
    elif ph <= 10:
        q_ph = 228 - 27 * ph
    elif ph <= 12:
        q_ph = 633 - 106.5 * ph + 4.5 * ph**2
    else:
        q_ph = 3.0
    p_ph = q_ph**w["ph"]

    # ---------- 4) DBO ----------
    if 0 < dbo <= 5:
        q_dbo = 99.96 * math.exp(-0.1232728 * dbo)
    elif dbo <= 15:
        q_dbo = 104.67 - 31.5463 * math.log10(dbo)
    elif dbo <= 30:
        q_dbo = 4394.91 * dbo**-1.99809
    else:
        q_dbo = 2.0
    p_dbo = q_dbo**w["dbo"]

    # ---------- 5) Nitrogênio Total ----------
    if 0 < nitrogenio_total <= 10:
        q_nt = 100 - 8.169 * nitrogenio_total + 0.3059 * nitrogenio_total**2
    elif nitrogenio_total <= 60:
        q_nt = 101.9 - 23.1023 * math.log10(nitrogenio_total)
    elif nitrogenio_total <= 100:
        q_nt = 159.3148 * math.exp(-0.0512842 * nitrogenio_total)
    else:
        q_nt = 1.0
    p_nt = q_nt**w["nt"]

    # ---------- 6) Fósforo Total ----------
    if 0 < fosforo_total <= 1:
        q_ft = 99 * math.exp(-0.91629 * fosforo_total)
    elif fosforo_total <= 5:
        q_ft = 57.6 - 20.178 * fosforo_total + 2.1326 * fosforo_total**2
    elif fosforo_total <= 10:
        q_ft = 19.8 * math.exp(-0.13544 * fosforo_total)
    else:
        q_ft = 5.0
    p_ft = q_ft**w["ft"]

    # ---------- 7) Turbidez ----------
    if 0 < turbidez <= 25:
        q_tb = 100.17 - 2.67 * turbidez + 0.03775 * turbidez**2
    elif turbidez <= 100:
        q_tb = 84.76 * math.exp(-0.016206 * turbidez)
    else:
        q_tb = 5.0
    p_tb = q_tb**w["tb"]

    # ---------- 8) Sólidos Totais ----------
    if 0 < solidos_totais <= 150:
        q_st = 79.75 + 0.166 * solidos_totais - 0.001088 * solidos_totais**2
    elif solidos_totais <= 500:
        q_st = 101.67 - 0.13917 * solidos_totais
    else:
        q_st = 32.0
    p_st = q_st**w["st"]

    # ---------- 9) Temperatura (peso fixo salvo se sobrescrito) ----------
    p_temp = 94.0**w["temp"]

    # ---------- Cálculo do IQA ----------
    iqa = (
        p_od
        * p_cf
        * p_ph
        * p_dbo
        * p_nt
        * p_ft
        * p_temp
        * p_tb
        * p_st
    )

    # ---------- Classificação ----------
    if iqa <= 19:
        classe = "Péssima"
    elif iqa <= 36:
        classe = "Ruim"
    elif iqa <= 51:
        classe = "Regular"
    elif iqa <= 79:
        classe = "Boa"
    else:
        classe = "Ótima"

    return {"iqa": round(iqa, 2), "qualidade": classe}
