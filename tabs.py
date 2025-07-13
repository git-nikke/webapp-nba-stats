import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import execute_query, get_all_players

def create_tab_medie_stagione():
    seasons = [
        "dunkest_stats_2018_19",
        "dunkest_stats_2019_20",
        "dunkest_stats_2020_21",
        "dunkest_stats_2021_22",
        "dunkest_stats_2022_23",
        "dunkest_stats_2023_24",
        "dunkest_stats_2024_25",
    ]
    season = st.selectbox("Season", seasons)

    stats = [
        'slug', 'position', 'team_code', 'pdk', 'gp', 'min', 'starter', 'pts', 'ast',
        'reb', 'dreb', 'oreb', 'stl', 'blk', 'blka','tov', 'fgm', 'fga', 'fgp', 'tpm',
        'tpa', 'tpp', 'ftm', 'fta', 'ftp', 'pf', 'plus_minus'
    ]
    stat = st.selectbox("Statistica Ordine", stats)
    AorD = st.selectbox("Ordine", ["DESC", "ASC"])
    gp = st.slider("Min GP", 0, 82)

    query = f"""
        SELECT 
            slug AS NAME,
            position AS POS,
            team_code AS TEAM,
            pdk AS PDK,
            gp AS GP,
            min AS MIN,
            starter AS STARTER,
            pts AS PTS,
            ast AS AST,
            reb AS REB,
            dreb AS DREB,
            oreb AS OREB,
            stl AS STL,
            blk AS BLK,
            blka AS BLKA,
            tov AS TOV,
            fgm AS FGM,
            fga AS FGA,
            fgp AS FGP,
            tpm AS TPM,
            tpa AS TPA,
            tpp AS TPP,
            ftm AS FTM,
            fta AS FTA,
            ftp AS FTP,
            pf AS PF,
            plus_minus AS PLUS_MINUS
        FROM {season}
        WHERE gp > {gp}
        ORDER BY {stat} {AorD};
    """

    avgquery = f"""
        SELECT 
            AVG(gp) AS GP,
            avg(pdk) AS PDK,
            AVG(pts) AS PTS,
            AVG(ast) AS AST,
            AVG(reb) AS REB,
            AVG(stl) AS STL,
            AVG(blk) AS BLK
        FROM {season}
        WHERE gp > {gp};
    """

    result = execute_query(st.session_state["connection"], query)
    df = pd.DataFrame(result.fetchall(), columns=result.keys()).round(2)
    st.dataframe(df, use_container_width=True)

    avgresult = execute_query(st.session_state["connection"], avgquery)
    avgrow = dict(zip(avgresult.keys(), avgresult.fetchone()))

    cols = st.columns(7)
    for i, key in enumerate(["GP", "PDK", "PTS", "AST", "REB", "STL", "BLK"]):
        cols[i].metric(key, f"{avgrow[key]:.2f}")

def create_tab_giocatore():
    seasons = [
        "dunkest_stats_2018_19",
        "dunkest_stats_2019_20",
        "dunkest_stats_2020_21",
        "dunkest_stats_2021_22",
        "dunkest_stats_2022_23",
        "dunkest_stats_2023_24",
        "dunkest_stats_2024_25",
    ]

    player_list = get_all_players()
    query = st.text_input("Inserisci parte del nome giocatore")
    filtered_players = [p for p in player_list if query.lower() in p.lower()] if query else []

    if filtered_players:
        player_name = st.selectbox("Seleziona giocatore corrispondente:", filtered_players)
    else:
        st.info("Nessun giocatore trovato")
        return

    df_all = pd.DataFrame()
    for season in seasons:
        query = f"""
            SELECT 
                '{season}' as SEASON,
                slug AS NAME,
                position AS POS,
                team_code AS TEAM,
                pdk AS PDK,
                gp AS GP,
                min AS MIN,
                starter AS STARTER,
                pts AS PTS,
                ast AS AST,
                reb AS REB,
                dreb AS DREB,
                oreb AS OREB,
                stl AS STL,
                blk AS BLK,
                blka AS BLKA,
                tov AS TOV,
                fgm AS FGM,
                fga AS FGA,
                fgp AS FGP,
                tpm AS TPM,
                tpa AS TPA,
                tpp AS TPP,
                ftm AS FTM,
                fta AS FTA,
                ftp AS FTP,
                pf AS PF,
                plus_minus AS PLUS_MINUS
            FROM {season}
            WHERE slug = :player AND gp > 0;
        """
        result = execute_query(st.session_state["connection"], query, {"player": player_name})
        df_temp = pd.DataFrame(result.fetchall(), columns=result.keys())
        df_all = pd.concat([df_all, df_temp], ignore_index=True)

    df_all["SEASON"] = df_all["SEASON"].str.extract(r"dunkest_stats_(\d{4})_(\d{2})").apply(lambda x: f"{x[0][-2:]}/{x[1]}", axis=1)
    st.dataframe(df_all, use_container_width=True)

    if not df_all.empty:
        seasons_a = ['18/19', '19/20', '20/21', '21/22', '22/23', '23/24', '24/25']
        weights = [0.14, 0.28, 0.32, 0.46, 0.60, 0.74, 1.00]
        df_ws = df_all.copy()
        for season_a, weight in zip(seasons_a, weights):
            df_ws.loc[df_ws["SEASON"] == season_a, "PDK"] *= weight
        # Ora calcolare il valore finale di PDK ponderato
        total_weight = sum(weights)
        weighted_pdk = sum(df_ws["PDK"]) / total_weight

        stats_to_avg = ["GP", "PDK", "PTS", "AST", "REB", "STL", "BLK"]
        avg_values = df_all[stats_to_avg].mean()

        st.markdown("#### Media nelle 7 stagioni più recenti")
        cols = st.columns(len(stats_to_avg)+2)
        for i, stat in enumerate(stats_to_avg):
            cols[i].metric(stat, f"{avg_values[stat]:.2f}")
        cols[7].metric("PDK pond", f"{weighted_pdk:.2f}")

        if weighted_pdk > avg_values["PDK"]:
            icon = "↗️"
            color = "normal"
        else:
            icon = "↘️"
            color = "inverse"

        cols[8].metric(label="trend", value=f"{(weighted_pdk - avg_values['PDK']):.2f}", delta=f"{icon}", delta_color=color)

    stats = ["GP", "PDK", "PTS", "AST", "REB", "STL", "BLK"]
    selected = st.multiselect("Seleziona statistiche da visualizzare", stats, default=stats)

    if selected:
        df_plot = df_all[["SEASON"] + selected].sort_values("SEASON")
        df_melted = df_plot.melt(id_vars="SEASON", var_name="Statistica", value_name="Valore")
        fig = px.line(df_melted, x="SEASON", y="Valore", color="Statistica", markers=True, title=f"Andamento Statistiche: {player_name}")
        fig.update_layout(title_x=0.5, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)