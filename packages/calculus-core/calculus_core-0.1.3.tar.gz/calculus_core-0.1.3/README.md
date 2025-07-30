# Calculus-Core

![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)

**Calculus-Core** é uma biblioteca e ferramenta de engenharia geotécnica para o cálculo de capacidade de carga em fundações profundas (estacas). O projeto implementa métodos de cálculo semi-empíricos consagrados na literatura técnica brasileira e oferece múltiplas formas de interação, incluindo uma interface web interativa.

---

### Tabela de Conteúdos
1.  [Principais Funcionalidades](#principais-funcionalidades)
2.  [Instalação](#instalação)
3.  [Como Usar](#como-usar)
    - [Como uma Biblioteca Python](#1-como-uma-biblioteca-python)
    - [Pela Interface Web (Streamlit)](#2-pela-interface-web-streamlit)
4.  [Métodos Implementados](#métodos-implementados)
5.  [Desenvolvimento](#desenvolvimento)
6.  [Licença](#licença)

---

## Principais Funcionalidades

- **Múltiplos Métodos de Cálculo:** Implementação dos métodos de Aoki-Velloso (1975), Aoki-Velloso revisado por Laprovitera (1998), Décourt-Quaresma (1978) e Teixeira (1996).
- **Interface Web Interativa:** Uma aplicação construída com [Streamlit](https://streamlit.io/) para facilitar a entrada de dados e a visualização dos resultados de forma amigável.
- **Estrutura Modular:** O código é organizado como um pacote Python instalável, permitindo que as suas funcionalidades sejam facilmente importadas e utilizadas noutros projetos.

---

## Instalação

Pode instalar o `calculus-core` diretamente do PyPI usando `pip`:

```bash
pip install calculus-core
```

## Métodos alternativos

### Astral uv

Siga os passos conforme a [documentação](https://docs.astral.sh/uv/getting-started/installation/).

### Windows

Abra o terminal PowerShell e execute o código abaixo.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS e Linux

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Instalando para utilizar como biblioteca em projeto

1. Inicie um projeto

```sh
uv init <nome-do-seu-projeto>
```

2. Acesse a pasta do projeto

```
cd <nome-do-seu-projeto>
```

3. Instale o pacote com uv:

Use o uv para instalar diretamente do `PyPI`

```sh
uv add calculus-core
```

Ou diretamente pelo repósitorio

```sh
uv add https://github.com/kaiosilva-dataeng/calculus-core.git
```

### Instalando como ferramental para acesso da GUI no path global.

Use o uv para instalar diretamente do `PyPI`

```sh
uv tool install calculus-core
```

Ou diretamente pelo repósitorio

```sh
uv tool install https://github.com/kaiosilva-dataeng/calculus-core.git
```

## Como usar

O `calculus-core` pode ser utilizado de três formas distintas:

### 1. Como uma Biblioteca Python

Importe e utilize as classes e funções do pacote nos seus próprios scripts Python. Este é o método ideal para automação e integração com outras ferramentas.

**Exemplo:**

Importe e utilize as classes e funções do pacote nos seus próprios scripts Python. Este é o método ideal para automação e integração com outras ferramentas.

```python
# Faça a importação do objeto referente ao método de cálculo desejado
from calculus_core.aoki_velloso import aoki_velloso_1975
# Importe os models de Estaca e PerfilSPT
from calculus_core.models import Estaca, PerfilSPT

# Crie uma instancia do perfil SPT e adicione as camadas de solo.
perfil_spt = PerfilSPT()
perfil_spt.adicionar_medidas(
    [
        (1, 3, 'argila_arenosa'),
        (2, 3, 'argila_arenosa'),
        (3, 5, 'argila_arenosa'),
        (4, 6, 'argila_arenosa'),
        (5, 8, 'argila_arenosa'),
        (6, 13, 'areia_argilosa'),
        (7, 17, 'areia_argilosa'),
        (8, 25, 'areia_argilosa'),
        (9, 27, 'areia_silto_argilosa'),
        (10, 32, 'areia_silto_argilosa'),
        (11, 36, 'areia_silto_argilosa'),
    ]
)

# Crie uma instancia da estaca
estaca = Estaca(
    tipo='pré-moldada',
    processo_construcao='deslocamento',
    formato='quadrada',
    secao_transversal=0.3,
    cota_assentamento=10,
)

# Execute o cálculo
resultado = aoki_velloso_1975.calcular(perfil_spt, estaca)
print(resultado)
```

Veja mais exemplos em [Notebooks](notebooks).

### 2. Pela Interface Web (Streamlit)

Para uma experiência mais visual e interativa, utilize a aplicação web. É ideal para verificações rápidas e para utilizadores que não são programadores.

Para iniciar a aplicação, execute o seguinte comando no seu terminal:

```sh
calculus-app
```

O seu navegador abrirá automaticamente com a interface da aplicação.

![Screenshot da Aplicação](docs/interface-web.png)

# Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

# Créditos

Desenvolvido como projeto de conclusão de curso de Engenharia Civil pelo IFTO - Campus Palmas.
Por [Kaio Henrique Pires da Silva](https://www.linkedin.com/in/kaiosilva-dataeng/)
