# 🚀 Simulador Financeiro Imobiliário Completo

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-red?style=for-the-badge&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Ativo-brightgreen?style=for-the-badge)

Uma aplicação web interativa e para análise de financiamento imobiliário, construída com Python e Streamlit.
---

### 🔗 **[Clique aqui para acessar a aplicação ao vivo!](https://simulador-imobiliario-robson.streamlit.app/)**

---

## ✨ Principais Funcionalidades

Este simulador oferece uma visão 360° da compra de um imóvel, permitindo ao usuário analisar diversos cenários e estratégias:

* **📊 Simulação de Financiamento Detalhada:**
    * Compare os sistemas de amortização **SAC** e **Price**.
    * Visualize gráficos interativos da evolução do saldo devedor, composição das parcelas e juros acumulados.

* **🤔 Análise Estratégica: Comprar vs. Alugar:**
    * Simule a evolução do seu patrimônio líquido ao longo de décadas, comparando o cenário de compra com o de aluguel.
    * Descubra o "ponto de equilíbrio", o momento em que a compra se torna financeiramente mais vantajosa.
    * Leve em conta todos os custos: ITBI, cartório, condomínio, IPTU, valorização do imóvel e rendimento dos investimentos.

* **🏗️ Simulação de Compra na Planta:**
    * Modele o financiamento de um imóvel em construção com inputs detalhados para **Ato, parcelas mensais e balões anuais**.
    * Analise o impacto da correção pelo **INCC** no valor final do imóvel e no saldo a financiar.

* **💡 Cenários de Otimização:**
    * **"Bola de Neve":** Simule o impacto de aportes mensais extras e veja quantos anos e centenas de milhares de reais em juros você pode economizar.
    * **Amortização Pontual vs. Investir:** Analise se é melhor usar um dinheiro extra (13º, bônus) para abater a dívida ou para investir, com base nas taxas do seu financiamento e no rendimento estimado da sua carteira.

* **📄 Geração de Relatórios em PDF:**
    * Crie um relatório personalizado em PDF com um resumo completo de todas as análses realizadas, pronto para ser salvo ou compartilhado.

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias e bibliotecas:

* **Backend & Lógica:** Python 3.10+
* **Interface Web:** Streamlit
* **Manipulação de Dados:** Pandas
* **Gráficos Interativos:** Plotly Express
* **Gráficos para PDF:** Matplotlib
* **Geração de PDF:** FPDF2
* **Versionamento:** Git & GitHub

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para rodar a aplicação no seu próprio computador.

### Pré-requisitos
* Python 3.10 ou superior
* Git

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/](https://github.com/)[SEU-USUARIO]/simulador-imobiliario.git
    cd simulador-imobiliario
    ```

2.  **Crie e ative um ambiente virtual (Recomendado):**
    ```bash
    # Para Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run app.py
    ```
    A aplicação abrirá automaticamente no seu navegador padrão.

## 📁 Estrutura do Projeto

```
simulador-imobiliario/
├── assets/
│   └── icone.png         # Ícone usado na aplicação
├── app.py                # Todo o código da aplicação Streamlit
├── requirements.txt      # Lista de dependências Python
└── README.md             # Este arquivo
```

## 🤝 Como Contribuir

Contribuições são bem-vindas! Se você tem ideias para novas funcionalidades ou encontrou algum bug, sinta-se à vontade para:

1.  Fazer um **Fork** deste repositório.
2.  Criar uma nova **Branch** (`git checkout -b feature/sua-feature`).
3.  Fazer o **Commit** das suas mudanças (`git commit -m 'Adiciona nova feature'`).
4.  Fazer o **Push** para a Branch (`git push origin feature/sua-feature`).
5.  Abrir um **Pull Request**.


**Desenvolvido por Robson Ricardo da Silva**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/robson-ricardo/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Robson-RSilva)