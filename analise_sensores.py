import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Configuração inicial do Streamlit
st.set_page_config(layout="wide", page_title="Dashboard de Sensores Ambientais")

st.title("Dashboard de Análise de Sensores Ambientais")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Carregue o arquivo CSV (separador ';')", type=["csv"])

if uploaded_file is not None:
    # Ler o arquivo CSV
    data = pd.read_csv(uploaded_file, delimiter=';', encoding='ISO-8859-1')
    data['Concentracao'] = pd.to_numeric(data['Concentracao'], errors='coerce').fillna(0)
    st.success("Dados carregados com sucesso!")

    # Exibir os primeiros dados
    if st.checkbox("Exibir os primeiros registros do arquivo"):
        st.dataframe(data.head())

    # Opções de análise
    opcao = st.selectbox(
        "Selecione o tipo de análise:",
        ["Todos os Estados", "Todos os Municípios", "Analisar por Estado", "Analisar por Município"]
    )

    # Layout de métricas resumidas
    if opcao in ["Todos os Estados", "Todos os Municípios"]:
        st.markdown("### Métricas Resumidas")
        total_itens = data['Item_monitorado'].nunique()
        total_municipios = data['Nome do Município'].nunique()
        concentracao_media = data['Concentracao'].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Itens Monitorados", total_itens)
        col2.metric("Municípios", total_municipios)
        col3.metric("Concentração Média", f"{concentracao_media:.2f}")

    # Todos os Estados
    if opcao == "Todos os Estados":
        estados = data['Estado'].unique()
        st.write("Estados disponíveis:")
        st.write(", ".join(estados))

        for estado in estados:
            filtro = data[data['Estado'] == estado]
            concentracao_por_item = filtro.groupby('Item_monitorado')['Concentracao'].sum()

            # Filtrar valores negativos
            concentracao_por_item = concentracao_por_item[concentracao_por_item > 0]

            if not concentracao_por_item.empty:
                st.markdown(f"### Gráficos para o Estado: {estado}")
                col1, col2, col3 = st.columns(3)

                # Gráfico de barras
                with col1:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    concentracao_por_item.plot(
                        kind='bar',
                        ax=ax,
                        color='skyblue',
                        edgecolor='black',
                        width=0.6
                    )
                    ax.set_title("Concentração por Item")
                    ax.set_xlabel("Item Monitorado")
                    ax.set_ylabel("Concentração Total")
                    plt.xticks(rotation=90)
                    plt.tight_layout()
                    st.pyplot(fig)

                # Gráfico de linha
                with col2:
                    filtro['Data'] = pd.to_datetime(filtro['Data'], errors='coerce')
                    concentracao_por_data = filtro.groupby('Data')['Concentracao'].sum()

                    fig, ax = plt.subplots(figsize=(6, 4))
                    concentracao_por_data.plot(kind='line', ax=ax, marker='o', color='orange')
                    ax.set_title("Tendência de Concentração")
                    ax.set_xlabel("Data")
                    ax.set_ylabel("Concentração Total")
                    plt.grid()
                    plt.tight_layout()
                    st.pyplot(fig)

                # Gráfico de pizza
                with col3:
                    # Gráfico de pizza com legenda ao lado e porcentagens
                    fig, ax = plt.subplots(figsize=(8, 6))
                    colors = sns.color_palette("pastel")

                    # Criando o gráfico de pizza
                    concentracao_por_item.plot(
                        kind='pie',
                        colors=colors,
                        startangle=90,
                        labels=None,  # Remove os rótulos do gráfico
                        autopct=None,  # Remove os percentuais do gráfico
                        ax=ax
                    )
                    ax.set_ylabel("")  # Remove o título do eixo Y
                    ax.set_title("Distribuição por Item", fontsize=14)

                    # Calculando porcentagens
                    porcentagens = (concentracao_por_item / concentracao_por_item.sum()) * 100
                    legendas = [
                        f"{item} - {porcentagem:.1f}%" for item, porcentagem in
                        zip(concentracao_por_item.index, porcentagens)
                    ]

                    # Adicionando legenda ao lado
                    ax.legend(
                        labels=legendas,  # Nomes dos itens com porcentagem
                        loc="center left",
                        bbox_to_anchor=(1, 0.5),  # Posiciona ao lado direito do gráfico
                        title="Itens Monitorados",
                        fontsize=10,
                        title_fontsize=12
                    )

                    st.pyplot(fig)

            else:
                st.warning(f"O estado '{estado}' não possui valores positivos para concentração.")

    # Análise de Todos os Municípios
    elif opcao == "Todos os Municípios":
        municipios = data['Nome do Município'].unique()
        st.write("Municípios disponíveis:")
        st.write(", ".join(municipios))

        concentracao_por_municipio = data.groupby('Nome do Município')['Concentracao'].sum()

        # Filtrar valores negativos
        concentracao_por_municipio = concentracao_por_municipio[concentracao_por_municipio > 0]

        if not concentracao_por_municipio.empty:
            col1, col2, col3 = st.columns(3)

            # Gráfico de barras
            with col1:
                fig, ax = plt.subplots(figsize=(6, 4))
                concentracao_por_municipio.sort_values(ascending=False).plot(
                    kind='bar',
                    ax=ax,
                    color='green',
                    edgecolor='black',
                    width=0.6
                )
                ax.set_title("Concentração por Município")
                ax.set_xlabel("Município")
                ax.set_ylabel("Concentração Total")
                plt.xticks(rotation=90)
                plt.tight_layout()
                st.pyplot(fig)

            # Gráfico de pizza
            with col3:
                # Gráfico de pizza com legenda ao lado e porcentagens
                fig, ax = plt.subplots(figsize=(8, 6))
                colors = sns.color_palette("pastel")

                # Criando o gráfico de pizza
                concentracao_por_municipio.plot(
                    kind='pie',
                    colors=colors,
                    startangle=90,
                    labels=None,  # Remove os rótulos do gráfico
                    autopct=None,  # Remove os percentuais do gráfico
                    ax=ax
                )
                ax.set_ylabel("")  # Remove o título do eixo Y
                ax.set_title("Distribuição por Item", fontsize=14)

                # Calculando porcentagens
                porcentagens = (concentracao_por_municipio / concentracao_por_municipio.sum()) * 100
                legendas = [
                    f"{item} - {porcentagem:.1f}%" for item, porcentagem in
                    zip(concentracao_por_municipio.index, porcentagens)
                ]

                # Adicionando legenda ao lado
                ax.legend(
                    labels=legendas,  # Nomes dos itens com porcentagem
                    loc="center left",
                    bbox_to_anchor=(1, 0.5),  # Posiciona ao lado direito do gráfico
                    title="Itens Monitorados",
                    fontsize=10,
                    title_fontsize=12
                )

                st.pyplot(fig)

        else:
            st.warning("Nenhum município possui valores positivos para concentração.")

    # Analisar por Estado
    elif opcao == "Analisar por Estado":  # Alinhado corretamente com o bloco principal
        estado = st.text_input("Digite o estado (sigla):").strip().upper()
        if estado:
            filtro = data[data['Estado'] == estado]
            concentracao_por_item = filtro.groupby('Item_monitorado')['Concentracao'].sum()

            # Filtrar valores negativos
            concentracao_por_item = concentracao_por_item[concentracao_por_item > 0]

            if not filtro.empty and not concentracao_por_item.empty:
                st.markdown(f"### Dados e Gráficos para o Estado: {estado}")
                st.dataframe(filtro)

                col1, col2, col3 = st.columns(3)

                # Gráfico de barras
                with col1:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    concentracao_por_item.plot(
                        kind='bar',
                        ax=ax,
                        color='skyblue',
                        edgecolor='black',
                        width=0.6
                    )
                    ax.set_title("Concentração por Item")
                    ax.set_xlabel("Item Monitorado")
                    ax.set_ylabel("Concentração Total")
                    plt.xticks(rotation=90)
                    plt.tight_layout()
                    st.pyplot(fig)

                # Gráfico de linha
                with col2:
                    filtro['Data'] = pd.to_datetime(filtro['Data'], errors='coerce')
                    concentracao_por_data = filtro.groupby('Data')['Concentracao'].sum()

                    fig, ax = plt.subplots(figsize=(6, 4))
                    concentracao_por_data.plot(kind='line', ax=ax, marker='o', color='orange')
                    ax.set_title("Tendência de Concentração")
                    ax.set_xlabel("Data")
                    ax.set_ylabel("Concentração Total")
                    plt.grid()
                    plt.tight_layout()
                    st.pyplot(fig)

                # Gráfico de pizza
                with col3:
                    # Gráfico de pizza com legenda ao lado e porcentagens
                    fig, ax = plt.subplots(figsize=(8, 6))
                    colors = sns.color_palette("pastel")

                    # Criando o gráfico de pizza
                    concentracao_por_item.plot(
                        kind='pie',
                        colors=colors,
                        startangle=90,
                        labels=None,  # Remove os rótulos do gráfico
                        autopct=None,  # Remove os percentuais do gráfico
                        ax=ax
                    )
                    ax.set_ylabel("")  # Remove o título do eixo Y
                    ax.set_title("Distribuição por Item", fontsize=14)

                    # Calculando porcentagens
                    porcentagens = (concentracao_por_item / concentracao_por_item.sum()) * 100
                    legendas = [
                        f"{item} - {porcentagem:.1f}%" for item, porcentagem in
                        zip(concentracao_por_item.index, porcentagens)
                    ]

                    # Adicionando legenda ao lado
                    ax.legend(
                        labels=legendas,  # Nomes dos itens com porcentagem
                        loc="center left",
                        bbox_to_anchor=(1, 0.5),  # Posiciona ao lado direito do gráfico
                        title="Itens Monitorados",
                        fontsize=10,
                        title_fontsize=12
                    )
                    st.pyplot(fig)
            else:
                st.warning(f"Não há valores positivos de concentração para o estado '{estado}'.")

        # Analisar por Município
        elif opcao == "Analisar por Município":  # Alinhado corretamente com o bloco if principal
            municipio = st.text_input("Digite o município:").strip()
            if municipio:
                filtro = data[data['Nome do Município'] == municipio]
                concentracao_por_item = filtro.groupby('Item_monitorado')['Concentracao'].sum()

                # Filtrar valores negativos
                concentracao_por_item = concentracao_por_item[concentracao_por_item > 0]

                if not filtro.empty and not concentracao_por_item.empty:
                    st.markdown(f"### Dados e Gráficos para o Município: {municipio}")
                    st.dataframe(filtro)

                    col1, col2, col3 = st.columns(3)

                    # Gráfico de barras
                    with col1:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        concentracao_por_item.plot(
                            kind='bar',
                            ax=ax,
                            color='skyblue',
                            edgecolor='black',
                            width=0.6
                        )
                        ax.set_title("Concentração por Item")
                        ax.set_xlabel("Item Monitorado")
                        ax.set_ylabel("Concentração Total")
                        plt.xticks(rotation=90)
                        plt.tight_layout()
                        st.pyplot(fig)

                    # Gráfico de linha
                    with col2:
                        filtro['Data'] = pd.to_datetime(filtro['Data'], errors='coerce')
                        concentracao_por_data = filtro.groupby('Data')['Concentracao'].sum()

                        fig, ax = plt.subplots(figsize=(6, 4))
                        concentracao_por_data.plot(kind='line', ax=ax, marker='o', color='orange')
                        ax.set_title("Tendência de Concentração")
                        ax.set_xlabel("Data")
                        ax.set_ylabel("Concentração Total")
                        plt.grid()
                        plt.tight_layout()
                        st.pyplot(fig)

                    # Gráfico de pizza
                    with col3:
                        # Gráfico de pizza com legenda ao lado e porcentagens
                        fig, ax = plt.subplots(figsize=(8, 6))
                        colors = sns.color_palette("pastel")

                        # Criando o gráfico de pizza
                        concentracao_por_item.plot(
                            kind='pie',
                            colors=colors,
                            startangle=90,
                            labels=None,  # Remove os rótulos do gráfico
                            autopct=None,  # Remove os percentuais do gráfico
                            ax=ax
                        )
                        ax.set_ylabel("")  # Remove o título do eixo Y
                        ax.set_title("Distribuição por Item", fontsize=14)

                        # Calculando porcentagens
                        porcentagens = (concentracao_por_item / concentracao_por_item.sum()) * 100
                        legendas = [
                            f"{item} - {porcentagem:.1f}%" for item, porcentagem in
                            zip(concentracao_por_item.index, porcentagens)
                        ]

                        # Adicionando legenda ao lado
                        ax.legend(
                            labels=legendas,  # Nomes dos itens com porcentagem
                            loc="center left",
                            bbox_to_anchor=(1, 0.5),  # Posiciona ao lado direito do gráfico
                            title="Itens Monitorados",
                            fontsize=10,
                            title_fontsize=12
                        )
                        st.pyplot(fig)
                else:
                    st.warning(f"Não há valores positivos de concentração para o município '{municipio}'.")
