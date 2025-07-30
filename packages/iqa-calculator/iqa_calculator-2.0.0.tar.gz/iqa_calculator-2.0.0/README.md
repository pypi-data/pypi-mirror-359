
# Calculadora de IQA

O pacote `Calculadora de IQA` fornece uma função para calcular o Índice de Qualidade da Água (IQA). Este índice é utilizado para avaliar a qualidade da água com base em diversos parâmetros físicos, químicos e biológicos.

## Instalação

Para instalar o pacote, use o comando pip:

```bash
pip install iqa_calculator
```

## Exemplo de Uso

Abaixo está um exemplo de como utilizar o pacote para calcular o Índice de Qualidade da Água:

```python
from IQA.iqa_calculator import IQA

# Definindo os parâmetros de entrada
oxigenio_dissolvido = 8.0  # mg/L
coliformes_fecais = 200  # NMP/100mL
ph = 7.0
dbo = 5.0  # Demanda Bioquímica de Oxigênio, mg/L
nitrogenio_total = 1.0  # mg/L
fosforo_total = 0.1  # mg/L
turbidez = 2.0  # NTU (Unidades Nefelométricas de Turbidez)
solidos_totais = 100  # mg/L
altitude = 100  # Opcional, metros
temperatura = 25  # Opcional, graus Celsius

# Calculando o Índice de Qualidade da Água
resultado = IQA(
    oxigenio_dissolvido=oxigenio_dissolvido,
    coliformes_fecais=coliformes_fecais,
    ph=ph,
    dbo=dbo,
    nitrogenio_total=nitrogenio_total,
    fosforo_total=fosforo_total,
    turbidez=turbidez,
    solidos_totais=solidos_totais,
    altitude=altitude,
    temperatura=temperatura
)

# Exibindo o resultado
print("Resultado do cálculo do IQA:")
print(f"IQA: {resultado['iqa']}")
print(f"Qualidade da água: {resultado['qualidade']}")
```

## Parâmetros

- `oxigenio_dissolvido`: Oxigênio dissolvido em mg/L.
- `coliformes_fecais`: Número de coliformes fecais em NMP/100mL.
- `ph`: Nível de pH da amostra de água.
- `dbo`: Demanda Bioquímica de Oxigênio em mg/L.
- `nitrogenio_total`: Nitrogênio total em mg/L.
- `fosforo_total`: Fósforo total em mg/L.
- `turbidez`: Turbidez da água em NTU.
- `solidos_totais`: Sólidos totais em mg/L.
- `altitude` (opcional): Altitude em metros.
- `temperatura` (opcional): Temperatura em graus Celsius.

## Saída

A função retorna um dicionário com as seguintes chaves:

- `iqa`: O Índice de Qualidade da Água calculado.
- `qualidade`: Uma descrição qualitativa da qualidade da água (por exemplo, "Boa", "Ruim").

## Licença

[Licença MIT](LICENSE)

## Contribuições

Contribuições, problemas e pedidos de funcionalidades são bem-vindos!



# WQI Calculator

The `WQI Calculator` package provides a function for calculating the Water Quality Index (WQI). This index is used to assess water quality based on various physical, chemical, and biological parameters.

## Installation

To install the package, use pip:

```bash
pip install iqa_calculator
```

## Usage Example

Here is an example of how to use the package to calculate the Water Quality Index:

```python
from IQA.iqa_calculator import WQI

# Define the input parameters
dissolved_oxygen = 8.0  # mg/L
fecal_coliforms = 200  # MPN/100mL
ph = 7.0
bod = 5.0  # Biochemical Oxygen Demand, mg/L
total_nitrogen = 1.0  # mg/L
total_phosphorus = 0.1  # mg/L
turbidity = 2.0  # NTU (Nephelometric Turbidity Units)
total_solids = 100  # mg/L
altitude = 100  # Optional, meters
temperature = 25  # Optional, Celsius

# Calculate the Water Quality Index
result = WQI(
    dissolved_oxygen=dissolved_oxygen,
    fecal_coliforms=fecal_coliforms,
    ph=ph,
    bod=bod,
    total_nitrogen=total_nitrogen,
    total_phosphorus=total_phosphorus,
    turbidity=turbidity,
    total_solids=total_solids,
    altitude=altitude,
    temperature=temperature
)

# Display the result
print("WQI Calculation Result:")
print(f"WQI: {result['iqa']}")
print(f"Water Quality: {result['qualidade']}")
```

## Parameters

- `dissolved_oxygen`: Dissolved oxygen in mg/L.
- `fecal_coliforms`: Number of fecal coliforms in MPN/100mL.
- `ph`: pH level of the water sample.
- `bod`: Biochemical Oxygen Demand in mg/L.
- `total_nitrogen`: Total nitrogen in mg/L.
- `total_phosphorus`: Total phosphorus in mg/L.
- `turbidity`: Turbidity of the water in NTU.
- `total_solids`: Total solids in mg/L.
- `altitude` (optional): Altitude in meters.
- `temperature` (optional): Temperature in Celsius.

## Output

The function returns a dictionary with the following keys:

- `iqa`: The calculated Water Quality Index.
- `quality`: A qualitative description of the water quality (e.g., "Good", "Poor").

## License

[MIT License](LICENSE)

## Contributions

Contributions, issues, and feature requests are welcome!
