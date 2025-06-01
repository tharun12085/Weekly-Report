import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Intern Progress Tracker", layout="wide")
st.title("📘 Intern Weekly Progress Tracker")

# 📤 Upload CSV
uploaded_file = st.file_uploader("📤 Upload CSV file with intern progress", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    expected_columns = {"Team ID", "Team Lead", "Intern Name", "Python", "APIs", "Machine Learning", "SQL", "Data Visualization"}
    if not expected_columns.issubset(df.columns):
        st.error("Uploaded CSV is missing one or more expected columns.")
        st.stop()

    topics = ["Python", "APIs", "Machine Learning", "SQL", "Data Visualization"]
    status_colors = {
        "Not Started": "🔴",
        "Partially Completed": "🟡",
        "Completed": "🟢"
    }

    # 🔢 Calculate team completion percentages
    team_summary = []
    for team_id in df["Team ID"].unique():
        team_df = df[df["Team ID"] == team_id]
        completed_count = 0
        total_possible = len(team_df) * len(topics)
        for topic in topics:
            completed_count += team_df[topic].value_counts().get("Completed", 0)
        completion_percent = round((completed_count / total_possible) * 100, 2)
        team_summary.append((team_id, completion_percent))

    # 🚫 No sorting — retain order from CSV
    ordered_teams = df["Team ID"].drop_duplicates().tolist()

    # 🧭 Sidebar: select a team
    team_selected = st.sidebar.selectbox("📌 Select a Team", ordered_teams)

    # 🌐 Show selected team info
    team_df = df[df["Team ID"] == team_selected]
    lead = team_df["Team Lead"].iloc[0]
    interns = team_df["Intern Name"].tolist()

    st.markdown(f"👨‍💼 **Team Lead:** `{lead}`")

    # 🔥 Progress Heatmap (Emoji only)
    st.markdown("### 🔥 Progress Heatmap")
    st.markdown("""
    **Legend:**  
    🟢 Completed &nbsp;&nbsp;&nbsp; 🟡 Partially Completed &nbsp;&nbsp;&nbsp; 🔴 Not Started &nbsp;&nbsp;&nbsp; ❓ Unknown
    """)

    heatmap_data = []
    for intern in interns:
        intern_row = team_df[team_df["Intern Name"] == intern]
        row = {"Intern": intern}
        completed = 0
        for topic in topics:
            status = intern_row[topic].values[0]
            emoji = status_colors.get(status, "❓")
            if emoji == "🟢":
                completed += 1
            row[topic] = emoji
        row["Completion %"] = round((completed / len(topics)) * 100, 2)
        heatmap_data.append(row)

    emoji_df = pd.DataFrame(heatmap_data)
    emoji_df = emoji_df.sort_values(by="Completion %", ascending=False).reset_index(drop=True)
    st.dataframe(emoji_df, use_container_width=True)

    # 📊 Intern Completion Bar Chart
    st.markdown("### 📊 Intern Completion Percentage")
    bar_fig = px.bar(
        emoji_df,
        x="Intern",
        y="Completion %",
        text="Completion %",
        color="Completion %",
        color_continuous_scale="viridis",
        title="Intern-wise Completion Percentage"
    )
    st.plotly_chart(bar_fig, use_container_width=True)

    # 🥧 Pie Chart: Overall course status
    st.markdown("### 🥧 Overall Course Completion Status")
    all_statuses = []
    for topic in topics:
        all_statuses.extend(team_df[topic].tolist())

    status_count = pd.Series(all_statuses).value_counts().rename_axis("Status").reset_index(name="Count")
    fig = px.pie(
        status_count,
        names="Status",
        values="Count",
        title="Course Progress Distribution",
        color_discrete_map={
            "Completed": "#2ecc71",
            "Partially Completed": "#f1c40f",
            "Not Started": "#e74c3c"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

    # 🏆 Team Ranking Table
    st.markdown("### 🏆 Team Completion Ranking")
    team_rank_df = pd.DataFrame(team_summary, columns=["Team ID", "Completion %"])
    st.dataframe(team_rank_df.sort_values(by="Completion %", ascending=False).reset_index(drop=True), use_container_width=True)

else:
    st.info("📂 Please upload a CSV file to begin.")
