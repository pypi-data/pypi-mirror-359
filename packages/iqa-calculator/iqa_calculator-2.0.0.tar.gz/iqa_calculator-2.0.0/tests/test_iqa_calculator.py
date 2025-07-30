import math
import pytest

from iqa.iqa_calculator import IQA, _parse_weights

# --------------------------------------------------------------------
# Cenários básicos (sem pesos explícitos)
# --------------------------------------------------------------------
def test_calc_iqa_default_values():
    """Altitude e temperatura padrão (200 m, 22 °C)."""
    resultado = IQA(
        oxigenio_dissolvido=8.0,
        coliformes_fecais=200,
        ph=7.0,
        dbo=5.0,
        nitrogenio_total=1.0,
        fosforo_total=0.1,
        turbidez=2.0,
        solidos_totais=100,
    )
    assert isinstance(resultado, dict)
    assert set(resultado) == {"iqa", "qualidade"}
    assert resultado["iqa"] >= 0


def test_calc_iqa_with_altitude_and_temperature():
    """Valores explícitos para altitude e temperatura."""
    resultado = IQA(
        oxigenio_dissolvido=9.0,
        coliformes_fecais=150,
        ph=6.5,
        dbo=4.0,
        nitrogenio_total=2.0,
        fosforo_total=0.5,
        turbidez=3.0,
        solidos_totais=120,
        altitude=100,
        temperatura=25,
    )
    assert isinstance(resultado, dict)
    assert set(resultado) == {"iqa", "qualidade"}
    assert resultado["iqa"] >= 0


def test_calc_iqa_extreme_values():
    """Parâmetros extremos para checar robustez numérica."""
    resultado = IQA(
        oxigenio_dissolvido=0.5,
        coliformes_fecais=100_000,
        ph=2.0,
        dbo=50.0,
        nitrogenio_total=80.0,
        fosforo_total=10.0,
        turbidez=200,
        solidos_totais=1000,
        altitude=5000,
        temperatura=50,
    )
    assert isinstance(resultado, dict)
    assert set(resultado) == {"iqa", "qualidade"}
    assert resultado["iqa"] >= 0

# --------------------------------------------------------------------
# Pesos personalizados
# --------------------------------------------------------------------
def test_calc_iqa_custom_weights_list():
    """Usa uma lista de 9 pesos (ordem oficial) e garante que o IQA muda."""
    pesos = [0.15, 0.17, 0.12, 0.10, 0.10, 0.10, 0.10, 0.08, 0.08]
    base = IQA(
        oxigenio_dissolvido=7.5,
        coliformes_fecais=300,
        ph=7.2,
        dbo=4.0,
        nitrogenio_total=1.5,
        fosforo_total=0.2,
        turbidez=5,
        solidos_totais=110,
    )
    custom = IQA(
        oxigenio_dissolvido=7.5,
        coliformes_fecais=300,
        ph=7.2,
        dbo=4.0,
        nitrogenio_total=1.5,
        fosforo_total=0.2,
        turbidez=5,
        solidos_totais=110,
        weights=pesos,
    )
    assert base["iqa"] != custom["iqa"]  # deve haver diferença


def test_calc_iqa_custom_weights_dict_partial():
    """Sobrescreve apenas um peso via dict parcial."""
    resultado = IQA(
        oxigenio_dissolvido=8.2,
        coliformes_fecais=180,
        ph=6.9,
        dbo=3.8,
        nitrogenio_total=1.2,
        fosforo_total=0.08,
        turbidez=4,
        solidos_totais=105,
        weights={"ph": 0.20},  # aumenta peso do pH
    )
    assert isinstance(resultado, dict)
    assert resultado["iqa"] >= 0

# --------------------------------------------------------------------
# Validação de erros
# --------------------------------------------------------------------
def test_weights_sequence_wrong_length():
    """Lista/tupla com tamanho diferente de 9 deve lançar ValueError."""
    with pytest.raises(ValueError):
        _parse_weights([0.1, 0.2])  # apenas 2 itens


def test_weights_dict_invalid_key():
    """Dict com chave desconhecida deve lançar KeyError."""
    with pytest.raises(KeyError):
        _parse_weights({"foo": 0.1})


def test_weights_invalid_type():
    """Tipo não suportado para 'weights' deve lançar TypeError."""
    with pytest.raises(TypeError):
        _parse_weights(42)  # int não é sequência nem mapeamento
