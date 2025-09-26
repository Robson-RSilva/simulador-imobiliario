import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

class FinanciamentoImobiliario:
    def __init__(self, valor_imovel: float, valor_entrada: float, taxa_juros_anual: float, prazo_anos: int,
                 tipo_correcao: str = 'Fixo', taxa_correcao_anual: float = 0.0):
        self.valor_imovel = valor_imovel; self.valor_entrada = valor_entrada; self.prazo_anos = prazo_anos
        self.valor_financiado = valor_imovel - valor_entrada
        self.taxa_juros_anual = taxa_juros_anual
        self.taxa_juros_mensal = (1 + taxa_juros_anual / 100)**(1/12) - 1
        self.prazo_meses = prazo_anos * 12
        self.tipo_correcao = tipo_correcao
        self.taxa_correcao_anual = taxa_correcao_anual
        self.taxa_correcao_mensal = (1 + taxa_correcao_anual / 100)**(1/12) - 1 if taxa_correcao_anual > 0 else 0
        self.tabela_sac = pd.DataFrame(); self.tabela_price = pd.DataFrame()
    def calcular_sac(self):
        if self.valor_financiado <= 0: return pd.DataFrame()
        saldo_devedor = self.valor_financiado; dados = []; amortizacao_constante_nominal = self.valor_financiado / self.prazo_meses
        for mes in range(1, self.prazo_meses + 1):
            correcao_monetaria = saldo_devedor * self.taxa_correcao_mensal; saldo_devedor += correcao_monetaria
            juros = saldo_devedor * self.taxa_juros_mensal; amortizacao = amortizacao_constante_nominal; prestacao = amortizacao + juros
            if saldo_devedor < amortizacao: amortizacao = saldo_devedor; prestacao = amortizacao + juros
            saldo_devedor -= amortizacao; saldo_devedor = max(0, saldo_devedor)
            dados.append({"Mês": mes, "Prestação": prestacao, "Juros": juros, "Amortização": amortizacao, "Correção Monetária": correcao_monetaria, "Saldo Devedor": saldo_devedor})
        self.tabela_sac = pd.DataFrame(dados); return self.tabela_sac
    def calcular_price(self):
        if self.valor_financiado <= 0: return pd.DataFrame()
        saldo_devedor = self.valor_financiado; dados = []; i = self.taxa_juros_mensal
        for mes in range(1, self.prazo_meses + 1):
            correcao_monetaria = saldo_devedor * self.taxa_correcao_mensal; saldo_devedor += correcao_monetaria
            meses_restantes = self.prazo_meses - mes + 1
            if i > 0: prestacao = saldo_devedor * (i * (1 + i)**meses_restantes) / ((1 + i)**meses_restantes - 1)
            else: prestacao = saldo_devedor / meses_restantes if meses_restantes > 0 else 0
            juros = saldo_devedor * i; amortizacao = prestacao - juros; saldo_devedor -= amortizacao; saldo_devedor = max(0, saldo_devedor)
            dados.append({"Mês": mes, "Prestação": prestacao, "Juros": juros, "Amortização": amortizacao, "Correção Monetária": correcao_monetaria, "Saldo Devedor": saldo_devedor})
        self.tabela_price = pd.DataFrame(dados); return self.tabela_price
    def simular_amortizacao_recorrente(self, aporte_extra_mensal: float, sistema: str):
        tabela_original = self.tabela_sac if sistema.lower() == 'sac' else self.tabela_price
        if tabela_original is None or tabela_original.empty: return None
        saldo_devedor = self.valor_financiado; meses_para_quitar, total_juros_pago = 0, 0
        prestacao_base = tabela_original['Prestação'].iloc[0] if sistema.lower() == 'price' else None
        amortizacao_base = tabela_original['Amortização'].iloc[0] if sistema.lower() == 'sac' else None
        while saldo_devedor > 0:
            meses_para_quitar += 1; juros_do_mes = saldo_devedor * self.taxa_juros_mensal; total_juros_pago += juros_do_mes
            amortizacao_normal = prestacao_base - juros_do_mes if sistema.lower() == 'price' else amortizacao_base
            amortizacao_total_mes = min(saldo_devedor, amortizacao_normal + aporte_extra_mensal); saldo_devedor -= amortizacao_total_mes
        economia_de_juros = tabela_original['Juros'].sum() - total_juros_pago
        return {"novo_prazo_meses": meses_para_quitar, "economia_juros": economia_de_juros, "novo_total_juros": total_juros_pago}
    def comparar_amortizacao_vs_investimento(self, sistema: str, valor_amortizacao: float, mes_amortizacao: int, taxa_rendimento_mensal_investimento: float):
        tabela_original = self.tabela_sac if sistema.lower() == 'sac' else self.tabela_price
        if tabela_original is None or tabela_original.empty or not (0 < mes_amortizacao <= self.prazo_meses): return None
        saldo_devedor_antes = tabela_original.loc[mes_amortizacao - 2, 'Saldo Devedor'] if mes_amortizacao > 1 else self.valor_financiado
        amortizacao_mes_normal = tabela_original.loc[mes_amortizacao -1, 'Amortização']; saldo_devedor_depois_parcela = saldo_devedor_antes - amortizacao_mes_normal
        novo_saldo_devedor = saldo_devedor_depois_parcela - valor_amortizacao; total_juros_original = tabela_original['Juros'].sum()
        juros_pagos_ate_agora = tabela_original.loc[:mes_amortizacao-1, 'Juros'].sum(); juros_futuros_amortizando = 0
        if novo_saldo_devedor > 0:
            if sistema.lower() == 'sac':
                amortizacao_constante = self.valor_financiado / self.prazo_meses; meses_restantes_novo = int(novo_saldo_devedor / amortizacao_constante); saldo_temp = novo_saldo_devedor
                for _ in range(meses_restantes_novo + 1): juros = saldo_temp * self.taxa_juros_mensal; juros_futuros_amortizando += juros; saldo_temp -= amortizacao_constante;
            else:
                prestacao_constante = tabela_original.loc[0, 'Prestação']; saldo_temp = novo_saldo_devedor
                while saldo_temp > 0:
                    juros = saldo_temp * self.taxa_juros_mensal
                    if (juros + saldo_temp) < prestacao_constante: juros_futuros_amortizando += juros; break
                    juros_futuros_amortizando += juros; amortizacao = prestacao_constante - juros; saldo_temp -= amortizacao
        economia_de_juros = total_juros_original - (juros_pagos_ate_agora + juros_futuros_amortizando)
        meses_restantes_original = self.prazo_meses - (mes_amortizacao - 1); i_invest = taxa_rendimento_mensal_investimento / 100
        valor_final_investimento = valor_amortizacao * (1 + i_invest)**meses_restantes_original; lucro_investimento = valor_final_investimento - valor_amortizacao
        return {"economia_juros": economia_de_juros, "lucro_investimento": lucro_investimento}
    
    @staticmethod
    def simular_compra_na_planta(valor_imovel_inicial, prazo_obra_meses, taxa_incc_mensal, pagamentos_construtora):
        i_incc = taxa_incc_mensal / 100
        total_pago_corrigido, total_pago_nominal = 0, 0
        cronograma = [0] * (prazo_obra_meses + 1)
        total_pos_chaves_nominal = 0

        for pg in pagamentos_construtora:
            if pg['valor'] > 0:
                # Acumula o valor nominal total para referência
                total_pago_nominal += pg['valor'] * pg.get('qtd', 1)
                
                # Processa pagamentos que ocorrem ANTES ou ATÉ a entrega das chaves
                if pg['tipo'] == 'ato':
                    cronograma[0] += pg['valor']
                elif pg['tipo'] == 'mensal':
                    for i in range(1, pg.get('qtd', 1) + 1):
                        if i <= prazo_obra_meses:
                            cronograma[i] += pg['valor']
                elif pg['tipo'] == 'anual':
                    for mes in pg.get('meses', []):
                        if mes <= prazo_obra_meses:
                            cronograma[mes] += pg['valor']
                # *** NOVO: Processa pagamentos PÓS-CHAVES ***
                elif pg['tipo'] == 'pos_chaves':
                    # Estes valores são nominais e não entram no cálculo de correção do INCC
                    total_pos_chaves_nominal += pg['valor'] * pg.get('qtd', 1)

        # Calcula o valor corrigido dos pagamentos feitos DURANTE a obra
        for mes in range(prazo_obra_meses + 1):
            pagamento_nominal = cronograma[mes]
            if pagamento_nominal > 0:
                total_pago_corrigido += pagamento_nominal * (1 + i_incc)**mes
        
        # O valor final do imóvel é corrigido pelo INCC até a entrega das chaves
        valor_imovel_final = valor_imovel_inicial * (1 + i_incc)**prazo_obra_meses
        
        # O total da entrada é a soma dos valores corrigidos (durante a obra) + os valores nominais (pós-obra)
        total_entrada_final = total_pago_corrigido + total_pos_chaves_nominal
        
        # O saldo a financiar é a diferença entre o valor final do imóvel e tudo que foi pago para a construtora
        saldo_a_financiar = valor_imovel_final - total_entrada_final
        
        return {
            "valor_imovel_final": valor_imovel_final, 
            "total_pago_corrigido": total_entrada_final, # Renomeado para refletir o total da entrada
            "saldo_a_financiar": saldo_a_financiar, 
            "total_pago_nominal": total_pago_nominal
        }

def analisar_comprar_vs_alugar(params):
    financiamento = FinanciamentoImobiliario(params['valor_imovel'], params['valor_entrada'], params['taxa_juros_anual'], params['prazo_anos'])
    tabela = financiamento.calcular_price()
    if tabela.empty: return pd.DataFrame() # Evita erro se não houver financiamento
    custo_aquisicao = (params['valor_imovel'] * params['itbi_percentual'] / 100) + params['custos_cartorio']
    custo_mensal_proprietario = tabela['Prestação'].mean() + params['condominio_mensal'] + (params['iptu_anual'] / 12)
    patrimonio_aluguel = params['valor_entrada'] + custo_aquisicao; custo_mensal_aluguel_atual = params['aluguel_mensal_inicial']; dados_evolucao = []
    for ano in range(1, params['horizonte_analise_anos'] + 1):
        valor_atual_imovel = params['valor_imovel'] * (1 + params['valorizacao_anual_imovel'] / 100)**ano
        mes_correspondente = min(ano * 12, financiamento.prazo_meses); saldo_devedor_atual = tabela.loc[mes_correspondente - 1, 'Saldo Devedor'] if mes_correspondente <= financiamento.prazo_meses else 0
        patrimonio_compra = valor_atual_imovel - saldo_devedor_atual; diferenca_mensal = custo_mensal_proprietario - custo_mensal_aluguel_atual
        if diferenca_mensal > 0: patrimonio_aluguel += diferenca_mensal * 12
        patrimonio_aluguel *= (1 + params['rendimento_anual_investimentos'] / 100)
        dados_evolucao.append({'Ano': ano, 'Patrimônio (Comprando)': patrimonio_compra, 'Patrimônio (Alugando)': patrimonio_aluguel})
        custo_mensal_aluguel_atual *= (1 + params['reajuste_anual_aluguel'] / 100)
    return pd.DataFrame(dados_evolucao)

class PDF(FPDF):
    def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs); self.WIDTH = 210; self.HEIGHT = 297
    def header(self): self.set_font('Arial', 'B', 16); self.cell(0, 10, 'Relatório de Análise Imobiliária', 0, 1, 'C'); self.set_font('Arial', '', 9); self.cell(0, 5, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C'); self.ln(10)
    def footer(self): self.set_y(-15); self.set_font('Arial', 'I', 8); self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    def chapter_title(self, title): self.set_font('Arial', 'B', 13); self.set_fill_color(230, 230, 230); self.cell(0, 10, f' {title}', 0, 1, 'L', True); self.ln(4)
    def key_value_row(self, key, value): self.set_font('Arial', 'B', 10); self.cell(70, 8, f'  {key}:', border=0); self.set_font('Arial', '', 10); self.cell(0, 8, str(value), border=0, ln=1)
    def conclusion(self, text): self.ln(2); self.set_font('Arial', 'I', 10); self.multi_cell(0, 5, f'Veredito: {text}'); self.ln(5)
    def create_table(self, header, data, widths):
        self.set_font('Arial', 'B', 9); self.set_fill_color(240, 240, 240)
        for i, h in enumerate(header): self.cell(widths[i], 7, h, 1, 0, 'C', True)
        self.ln(); self.set_font('Arial', '', 9)
        for row in data:
            for i, item in enumerate(row): self.cell(widths[i], 7, item, 1, 0, 'R')
            self.ln()
        self.ln(8)

def gerar_pdf_completo(st_session_state, fin_fixo, fig_financiamento, df_compra_aluguel, fig_compra_aluguel):
    pdf = PDF()
    pdf.add_page()
    
    pdf.chapter_title('1. Resumo do Financiamento Base (Taxa Fixa)')
    pdf.key_value_row("Valor do Imóvel", f"R$ {fin_fixo.valor_imovel:,.2f}")
    pdf.key_value_row("Valor Financiado", f"R$ {fin_fixo.valor_financiado:,.2f}")
    pdf.key_value_row("Taxa de Juros", f"{fin_fixo.taxa_juros_anual}% a.a. (Fixa)")
    pdf.key_value_row("Prazo", f"{fin_fixo.prazo_anos} anos")
    pdf.ln(5)
    header = ['Sistema', 'Primeira Parcela', 'Última Parcela', 'Total de Juros']
    data = [
        ['SAC', f"R$ {fin_fixo.tabela_sac['Prestação'].iloc[0]:,.2f}", f"R$ {fin_fixo.tabela_sac['Prestação'].iloc[-1]:,.2f}", f"R$ {fin_fixo.tabela_sac['Juros'].sum():,.2f}"],
        ['Price', f"R$ {fin_fixo.tabela_price['Prestação'].iloc[0]:,.2f}", f"R$ {fin_fixo.tabela_price['Prestação'].iloc[0]:,.2f}", f"R$ {fin_fixo.tabela_price['Juros'].sum():,.2f}"]
    ]
    pdf.create_table(header, data, [25, 50, 50, 55])
    
    if st_session_state.aporte_extra > 0 or st_session_state.valor_amortizacao > 0:
      pdf.chapter_title('2. Análises de Otimização Financeira')
    if st_session_state.aporte_extra > 0:
        resultado = fin_fixo.simular_amortizacao_recorrente(st_session_state.aporte_extra, 'price')
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 10, "  Otimização 'Bola de Neve'", 0, 1)
        pdf.key_value_row("Economia de Juros", f"R$ {resultado['economia_juros']:,.2f}")
        pdf.key_value_row("Novo Prazo", f"{resultado['novo_prazo_meses'] // 12} anos e {resultado['novo_prazo_meses'] % 12} meses")
    if st_session_state.valor_amortizacao > 0:
        resultado = fin_fixo.comparar_amortizacao_vs_investimento('price', st_session_state.valor_amortizacao, st_session_state.mes_amortizacao, st_session_state.taxa_investimento_mensal)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 10, "  Amortizar Pontualmente vs. Investir", 0, 1)
        pdf.key_value_row("Economia Amortizando", f"R$ {resultado['economia_juros']:,.2f}")
        pdf.key_value_row("Lucro Investindo", f"R$ {resultado['lucro_investimento']:,.2f}")
        veredicto = "Amortizar" if resultado['economia_juros'] > resultado['lucro_investimento'] else "Investir"
        pdf.conclusion(f"Para este cenário, a melhor opção é {veredicto}.")

    if not df_compra_aluguel.empty:
        pdf.add_page()
        pdf.chapter_title('3. Análise Estratégica: Comprar vs. Alugar')
        resultado_final_compra = df_compra_aluguel.iloc[-1]['Patrimônio (Comprando)']
        resultado_final_aluguel = df_compra_aluguel.iloc[-1]['Patrimônio (Alugando)']
        pdf.key_value_row("Horizonte de Análise", f"{len(df_compra_aluguel)} anos")
        pdf.key_value_row("Patrimônio Final (Comprando)", f"R$ {resultado_final_compra:,.2f}")
        pdf.key_value_row("Patrimônio Final (Alugando)", f"R$ {resultado_final_aluguel:,.2f}")
        vantagem = resultado_final_compra - resultado_final_aluguel
        veredicto_cva = f"COMPRAR foi R$ {vantagem:,.2f} mais vantajoso." if vantagem > 0 else f"ALUGAR foi R$ {-vantagem:,.2f} mais vantajoso."
        pdf.conclusion(veredicto_cva)
    
    pdf.add_page(orientation='L')
    pdf.chapter_title('4. Anexos Gráficos')
    
    with BytesIO() as img_buffer:
        fig_financiamento.savefig(img_buffer, format='png', dpi=200, bbox_inches='tight')
        img_width = pdf.w - 40 # Usar quase toda a largura da página paisagem
        x_pos = (pdf.w - img_width) / 2
        pdf.image(img_buffer, x=x_pos, y=None, w=img_width)
    
    pdf.ln(5) # Adiciona um pequeno espaço vertical

    # Gráfico 2: Comprar vs. Alugar
    if not df_compra_aluguel.empty:
        pdf.add_page(orientation='P') # Nova página retrato para o segundo gráfico
        pdf.chapter_title('5. Gráfico: Evolução do Patrimônio (Comprar vs. Alugar)')
        with BytesIO() as img_buffer:
            fig_compra_aluguel.savefig(img_buffer, format='png', dpi=200, bbox_inches='tight')
            img_width = pdf.w - 20 # Usar quase toda a largura da página retrato
            x_pos = (pdf.w - img_width) / 2
            pdf.image(img_buffer, x=x_pos, y=None, w=img_width)
            
    return bytes(pdf.output())

# ==============================================================================
# INTERFACE DO USUÁRIO (STREAMLIT)
# ==============================================================================
st.set_page_config(layout="wide", page_title="Simulador Financeiro Imobiliário")
st.title("Simulador Financeiro Imobiliário")


plt.style.use('ggplot')
    
plt.rcParams['figure.autolayout'] = True
st.sidebar.image("assets/icon.png", width=160)

# --- COLETA DE INPUTS NA SIDEBAR ---
with st.sidebar:
    st.header("1. Modalidade da Compra")
    tipo_compra = st.radio("Escolha a modalidade", ["Imóvel Pronto", "Imóvel na Planta"], label_visibility="collapsed")
    
    if tipo_compra == "Imóvel Pronto":
        valor_imovel = st.number_input("Valor do Imóvel (R$)", value=750000, step=10000, key="valor_imovel", help="Valor total do imóvel conforme avaliação ou preço de venda.")
        valor_entrada = st.number_input("Valor da Entrada (R$)", value=150000, step=5000, key="valor_entrada", help="Recursos próprios que você usará. Normalmente, os bancos exigem no mínimo 20% do valor do imóvel.")
    else:
        st.subheader("Dados da Construção")
        valor_imovel_planta = st.number_input("Valor do Imóvel (na planta) (R$)", value=600000, step=10000, help="O preço inicial do imóvel no momento do lançamento pela construtora.")
        prazo_obra = st.slider("Prazo da Obra (meses)", 12, 60, 36, help="Tempo estimado em meses que a construtora levará para entregar as chaves.")
        incc_mensal = st.slider("Taxa INCC Mensal (%)", 0.0, 2.0, 0.5, 0.05, help="Estimativa da correção mensal do seu saldo devedor com a construtora. Historicamente, o INCC varia entre 0.4% e 1% ao mês.")
        
        with st.expander("Detalhar Pagamento da Entrada na Planta"):
            ato = st.number_input("Valor do Ato (R$)", value=30000, help="Pagamento inicial feito na assinatura do contrato com a construtora.")
            st.markdown("---")
            mensais_qtd = st.number_input("Qtd. Parcelas Mensais (durante obra)", value=36, help="Número de parcelas pagas mensalmente durante a obra.")
            mensais_valor = st.number_input("Valor da Parcela Mensal (R$)", value=2500, help="Valor nominal de cada parcela mensal.")
            st.markdown("---")
            anuais_qtd = st.number_input("Qtd. Balões Anuais (durante obra)", value=2, help="Número de parcelas intermediárias, maiores, geralmente pagas uma vez por ano.")
            anuais_valor = st.number_input("Valor do Balão Anual (R$)", value=15000, help="Valor nominal de cada balão/parcela anual.")
            st.markdown("---")
            # --- NOVOS CAMPOS ADICIONADOS ---
            pos_chaves_qtd = st.number_input("Qtd. Parcelas Pós-Chaves", value=24, help="Número de parcelas pagas diretamente à construtora APÓS a entrega das chaves.")
            pos_chaves_valor = st.number_input("Valor da Parcela Pós-Chaves (R$)", value=1000, help="Valor nominal de cada parcela pós-chaves. Este valor não sofre correção do INCC.")
        
        # --- LÓGICA DE CÁLCULO ATUALIZADA ---
        pagamentos_planta = [
            {'tipo': 'ato', 'valor': ato}, 
            {'tipo': 'mensal', 'valor': mensais_valor, 'qtd': mensais_qtd}, 
            {'tipo': 'anual', 'valor': anuais_valor, 'meses': [12 * i for i in range(1, anuais_qtd + 1)]},
            {'tipo': 'pos_chaves', 'valor': pos_chaves_valor, 'qtd': pos_chaves_qtd} # Nova entrada
        ]
        resultado_planta = FinanciamentoImobiliario.simular_compra_na_planta(valor_imovel_planta, prazo_obra, incc_mensal, pagamentos_planta)
        valor_imovel = resultado_planta['valor_imovel_final']
        valor_entrada = resultado_planta['total_pago_corrigido']
    
    st.header("2. Parâmetros do Financiamento")
    prazo_anos = st.slider("Prazo (anos)", 5, 40, 30, help="Prazo total do financiamento com o banco. Prazo menor = parcela maior, mas economia gigante nos juros totais.")
    taxa_juros_fixa = st.slider("Taxa de Juros Anual (Fixa %)", 5.0, 20.0, 10.5, 0.1, help="Taxa de juros efetiva cobrada pelo banco. Em Set/2025, taxas para bons clientes giram em torno de Selic (ex: 9.5%) + 2%.")

    st.header("3. Parâmetros da Análise Estratégica")
    with st.expander("Configurar Cenário: Comprar vs. Alugar"):
        itbi = st.slider("ITBI (%)", 0.0, 5.0, 3.0, 0.1, help="Imposto municipal sobre a transmissão do imóvel. Varia de 2% a 3% na maioria das cidades.")
        cartorio = st.number_input("Custos de Cartório (R$)", 0, 50000, 8000, 500, help="Gastos com escritura e registro do imóvel. Varia bastante, mas uma estimativa de 1% do valor do imóvel é um bom começo.")
        condominio = st.number_input("Condomínio Mensal (R$)", 0, 10000, 700, 50, help="Custo mensal de condomínio do imóvel a ser comprado.")
        iptu = st.number_input("IPTU Anual (R$)", 0, 50000, 3000, 100, help="Imposto anual sobre a propriedade.")
        aluguel = st.number_input("Aluguel Mensal Inicial (R$)", 0, 20000, 3000, 100, help="Valor do aluguel de um imóvel similar ao que você pretende comprar.")
        reajuste_aluguel = st.slider("Reajuste Anual Aluguel (%)", 0.0, 15.0, 7.0, 0.5, help="Índice de reajuste do aluguel. Geralmente atrelado ao IGP-M ou IPCA.")
        valorizacao_imovel = st.slider("Valorização Anual do Imóvel (%)", -5.0, 20.0, 6.0, 0.5, help="Estimativa de quanto o imóvel irá valorizar por ano. A inflação (IPCA) é uma base conservadora.")
        rendimento_invest = st.slider("Rendimento Anual dos Investimentos (%)", 0.0, 25.0, 9.5, 0.5, help="Rendimento LÍQUIDO (após impostos) da sua carteira de investimentos. A Selic/CDI é um bom ponto de partida para Renda Fixa.")
        horizonte = st.slider("Horizonte de Análise (anos)", 5, 40, 20, 1, help="Período de tempo para a simulação comparativa.")

# --- CÁLCULOS PRINCIPAIS (FEITOS UMA ÚNICA VEZ, FORA DAS ABAS) ---
fin_fixo = FinanciamentoImobiliario(valor_imovel, valor_entrada, taxa_juros_fixa, prazo_anos)
fin_fixo.calcular_sac()
fin_fixo.calcular_price()

params_cva = {'valor_imovel': valor_imovel, 'valor_entrada': valor_entrada, 'taxa_juros_anual': taxa_juros_fixa, 'prazo_anos': prazo_anos, 'itbi_percentual': itbi, 'custos_cartorio': cartorio, 'condominio_mensal': condominio, 'iptu_anual': iptu, 'aluguel_mensal_inicial': aluguel, 'reajuste_anual_aluguel': reajuste_aluguel, 'valorizacao_anual_imovel': valorizacao_imovel, 'rendimento_anual_investimentos': rendimento_invest, 'horizonte_analise_anos': horizonte}
df_cva = analisar_comprar_vs_alugar(params_cva)


# --- EXIBIÇÃO NAS ABAS ---
tab1, tab2, tab3 = st.tabs(["Visão Geral e Gráficos", "Otimização e Cenários", "Estratégia: Comprar vs. Alugar"])
with tab1:
    st.header("Resumo do Financiamento Base")
    if tipo_compra == "Imóvel na Planta":
        with st.container(border=True):
            st.subheader("Simulação de Imóvel na Planta Concluída")
            col1, col2, col3 = st.columns(3)
            col1.metric("Valor Total da Entrada (Pago à Construtora)", f"R$ {resultado_planta['total_pago_corrigido']:,.2f}")
            col2.metric("Valor Final do Imóvel (Corrigido)", f"R$ {valor_imovel:,.2f}")
            col3.metric("Saldo a Financiar", f"R$ {fin_fixo.valor_financiado:,.2f}")
    col1, col2 = st.columns(2)
    with col1: st.metric("Primeira Parcela (SAC)", f"R$ {fin_fixo.tabela_sac.iloc[0]['Prestação']:,.2f}" if not fin_fixo.tabela_sac.empty else "N/A"); st.metric("Custo Total Juros (SAC)", f"R$ {fin_fixo.tabela_sac['Juros'].sum():,.2f}" if not fin_fixo.tabela_sac.empty else "N/A")
    with col2: st.metric("Parcela Fixa (Price)", f"R$ {fin_fixo.tabela_price.iloc[0]['Prestação']:,.2f}" if not fin_fixo.tabela_price.empty else "N/A"); st.metric("Custo Total Juros (Price)", f"R$ {fin_fixo.tabela_price['Juros'].sum():,.2f}" if not fin_fixo.tabela_price.empty else "N/A")
    st.header("Gráficos Comparativos do Financiamento"); col1, col2 = st.columns(2)
    with col1:
        df_saldo_devedor = pd.concat([fin_fixo.tabela_sac[['Mês', 'Saldo Devedor']].assign(Sistema='SAC'), fin_fixo.tabela_price[['Mês', 'Saldo Devedor']].assign(Sistema='Price')]);
        paleta_cores = {'SAC': '#ff4b4b', 'Price': "#7c0202"}
        fig_saldo = px.line(df_saldo_devedor, x='Mês', y='Saldo Devedor', color='Sistema', title='Evolução do Saldo Devedor', markers=False, color_discrete_map=paleta_cores); fig_saldo.update_layout(height=400); st.plotly_chart(fig_saldo, use_container_width=True)
    with col2:
        df_juros = pd.concat([fin_fixo.tabela_sac[['Mês']].assign(SAC=fin_fixo.tabela_sac['Juros'].cumsum()), fin_fixo.tabela_price[['Mês']].assign(Price=fin_fixo.tabela_price['Juros'].cumsum())]).melt(id_vars=['Mês'], var_name='Sistema', value_name='Juros Acumulados'); fig_juros = px.line(df_juros, x='Mês', y='Juros Acumulados', color='Sistema', title='Juros Pagos Acumulados', markers=False, color_discrete_map=paleta_cores); fig_juros.update_layout(height=400); st.plotly_chart(fig_juros, use_container_width=True)
with tab2:
    st.header("Análises de Otimização e Cenários"); col1, col2 = st.columns(2)
    with col1:
        st.subheader("Otimização 'Bola de Neve'"); aporte_extra = st.slider("Aporte Extra Mensal (R$)", 0, 5000, 500, 50, key='aporte_extra', help="Um valor fixo pago a mais todo mês para acelerar a quitação. Ex: Pagar R$500 extras por mês pode quitar seu financiamento 10 anos antes e economizar centenas de milhares em juros.")
        if aporte_extra > 0 and not fin_fixo.tabela_price.empty: resultado_bola_de_neve = fin_fixo.simular_amortizacao_recorrente(aporte_extra, 'price'); st.metric("Economia de Juros", f"R$ {resultado_bola_de_neve['economia_juros']:,.2f}"); st.metric("Novo Prazo", f"{resultado_bola_de_neve['novo_prazo_meses'] // 12}a {resultado_bola_de_neve['novo_prazo_meses'] % 12}m")
    with col2:
        st.subheader("Amortizar Pontual vs. Investir"); valor_amortizacao = st.number_input("Valor da Amortização Pontual (R$)", 0, 1000000, 25000, 1000, key='valor_amortizacao', help="Um valor único que você tem para abater a dívida (ex: 13º salário, bônus, FGTS).")
        mes_amortizacao = st.slider("Mês da Operação", 1, prazo_anos * 12, 24, key='mes_amortizacao');
        taxa_investimento_mensal = st.slider("Rendimento Mensal do Investimento (%)", 0.1, 2.0, 0.8, 0.05, key='taxa_investimento_mensal', help="Rendimento LÍQUIDO (após impostos). Renda Fixa (CDI a 10.5% a.a.) rende aprox. 0.7-0.8%/mês. Valores acima de 1.2%/mês são considerados muito otimistas/arriscados.")
        if valor_amortizacao > 0 and not fin_fixo.tabela_price.empty: resultado_amort_invest = fin_fixo.comparar_amortizacao_vs_investimento('price', valor_amortizacao, mes_amortizacao, taxa_investimento_mensal); st.metric("Economia Amortizando", f"R$ {resultado_amort_invest['economia_juros']:,.2f}"); st.metric("Lucro Investindo", f"R$ {resultado_amort_invest['lucro_investimento']:,.2f}", delta=f"{resultado_amort_invest['lucro_investimento'] - resultado_amort_invest['economia_juros']:+,.2f}", delta_color="normal")
with tab3:
    st.header("Análise Estratégica: Comprar vs. Alugar")
    if not df_cva.empty:
      patrimonio_compra = df_cva.iloc[-1]['Patrimônio (Comprando)']; patrimonio_aluguel = df_cva.iloc[-1]['Patrimônio (Alugando)']; st.subheader("Resultados da Análise"); col1, col2 = st.columns(2)
      with col1: st.metric("Patrimônio Final (Comprando)", f"R$ {patrimonio_compra:,.2f}")
      with col2: st.metric("Patrimônio Final (Alugando)", f"R$ {patrimonio_aluguel:,.2f}", delta=f"{patrimonio_aluguel - patrimonio_compra:+,.2f}")
      fig_cva = px.line(df_cva.melt(id_vars=['Ano'], var_name='Cenário', value_name='Patrimônio Líquido'), x='Ano', y='Patrimônio Líquido', color='Cenário', title='Evolução do Patrimônio Líquido: Comprar vs. Alugar', markers=True, color_discrete_map=paleta_cores, height=450); st.plotly_chart(fig_cva, use_container_width=True)

# --- BOTÃO DE PDF ---
st.sidebar.markdown("---"); st.sidebar.header("Relatório Final")
if st.sidebar.button("Gerar Relatório Completo em PDF"):
    with st.spinner("Criando seu relatório personalizado..."):
        # Criação das figuras Matplotlib para o PDF (sempre que o botão é clicado)
        fig_fin_pdf, axs = plt.subplots(1, 2, figsize=(11, 4))
        if not fin_fixo.tabela_price.empty:
            axs[0].plot(fin_fixo.tabela_sac['Mês'].to_numpy(), fin_fixo.tabela_sac['Saldo Devedor'].to_numpy(), label='SAC', color='#ff4b4b'); axs[0].plot(fin_fixo.tabela_price['Mês'].to_numpy(), fin_fixo.tabela_price['Saldo Devedor'].to_numpy(), label='Price', color='#0e1117'); axs[0].set_title('Saldo Devedor'); axs[0].legend(); axs[0].grid(True, alpha=0.5)
            axs[1].plot(fin_fixo.tabela_sac['Mês'].to_numpy(), fin_fixo.tabela_sac['Juros'].cumsum().to_numpy(), label='SAC', color='#ff4b4b'); axs[1].plot(fin_fixo.tabela_price['Mês'].to_numpy(), fin_fixo.tabela_price['Juros'].cumsum().to_numpy(), label='Price', color='#0e1117'); axs[1].set_title('Juros Acumulados'); axs[1].legend(); axs[1].grid(True, alpha=0.5)
        
        fig_cva_pdf, ax = plt.subplots(figsize=(11, 5))
        if not df_cva.empty:
            ax.plot(df_cva['Ano'].to_numpy(), df_cva['Patrimônio (Comprando)'].to_numpy(), label='Comprando', marker='o'); ax.plot(df_cva['Ano'].to_numpy(), df_cva['Patrimônio (Alugando)'].to_numpy(), label='Alugando', marker='o'); ax.set_title('Evolução do Patrimônio Líquido'); ax.legend(); ax.grid(True, alpha=0.5)
        
        pdf_bytes = gerar_pdf_completo(st.session_state, fin_fixo, fig_fin_pdf, df_cva, fig_cva_pdf)
        st.sidebar.download_button(label="Baixar Relatório PDF", data=pdf_bytes, file_name=f"relatorio_imobiliário_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")