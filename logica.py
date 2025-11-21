import pandas as pd
import numpy as np

def gerar_cenario_completo(n_skus=500, n_pedidos=100000):
    np.random.seed(42)

    # --- GERAÇÃO DE DADOS SINTÉTICOS ---
    skus = [f"SKU-{10000 + i}" for i in range(n_skus)]
    n_pesados = int(n_skus * 0.2)
    n_leves = n_skus - n_pesados

    pesos = np.concatenate([
        np.random.uniform(0.5, 5.0, n_leves),
        np.random.uniform(20.0, 80.0, n_pesados)
    ])

    df_dimensoes = pd.DataFrame({
        'SKU': skus,
        'Peso_kg': np.random.permutation(pesos)
    })

    # Configuração do Layout do Armazém
    n_locais = int(n_skus * 1.5)
    locais = [f"LOC-{str(i).zfill(4)}" for i in range(n_locais)]
    distancias = np.linspace(5, 100, n_locais)

    tipos_locais = np.concatenate([
        ["Prateleira Leve"] * int(n_locais * 0.8),
        ["Chão Pesado"] * int(n_locais * 0.2)
    ])
    np.random.shuffle(tipos_locais)

    df_layout = pd.DataFrame({
        'ID_Endereco': locais,
        'Distancia': distancias,
        'Tipo_Area': tipos_locais
    })

    # Simulação de Vendas (Distribuição Zipf para forçar Pareto/Curva ABC)
    probabilidades = np.array([1 / (i + 1) for i in range(n_skus)])
    probabilidades /= probabilidades.sum()

    vendas_skus = np.random.choice(skus, size=n_pedidos, p=probabilidades)
    df_vendas = pd.DataFrame({'SKU': vendas_skus}).value_counts().reset_index()
    df_vendas.columns = ['SKU', 'Qtd_Vendas']

    # --- PROCESSAMENTO (CENÁRIO AS-IS) ---
    df_full = df_vendas.merge(df_dimensoes, on='SKU')
    
    # Regra de Negócio: Pesados (>20kg) só podem ir para o Chão
    df_full['Tipo_Necessario'] = np.where(df_full['Peso_kg'] >= 20, 'Chão Pesado', 'Prateleira Leve')

    # Cálculo da Curva ABC
    df_full['Acumulado'] = df_full['Qtd_Vendas'].cumsum() / df_full['Qtd_Vendas'].sum()
    df_full['ABC'] = np.where(df_full['Acumulado'] <= 0.8, 'A', np.where(df_full['Acumulado'] <= 0.95, 'B', 'C'))

    # Simula alocação aleatória atual (Caos)
    df_full['Distancia_Atual'] = np.random.choice(df_layout['Distancia'], size=len(df_full))
    custo_atual = (df_full['Qtd_Vendas'] * df_full['Distancia_Atual']).sum() / 1000

    # --- OTIMIZAÇÃO (SLOTTING INTELIGENTE) ---
    leves = df_full[df_full['Tipo_Necessario'] == 'Prateleira Leve'].sort_values('Qtd_Vendas', ascending=False)
    pesados = df_full[df_full['Tipo_Necessario'] == 'Chão Pesado'].sort_values('Qtd_Vendas', ascending=False)

    locais_leves = df_layout[df_layout['Tipo_Area'] == 'Prateleira Leve'].sort_values('Distancia')
    locais_pesados = df_layout[df_layout['Tipo_Area'] == 'Chão Pesado'].sort_values('Distancia')

    # Algoritmo de Matchmaking: Melhor Produto -> Melhor Posição Disponível
    leves['Distancia_Nova'] = locais_leves['Distancia'].values[:len(leves)]
    pesados['Distancia_Nova'] = locais_pesados['Distancia'].values[:len(pesados)]

    df_otimizado = pd.concat([leves, pesados])
    custo_novo = (df_otimizado['Qtd_Vendas'] * df_otimizado['Distancia_Nova']).sum() / 1000

    return custo_atual, custo_novo, df_full, df_otimizado