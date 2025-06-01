import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Intern Progress Tracker", layout="wide")
st.title("📘 Intern Progress Tracker (Daily & Weekly)")

# Upload CSV
uploaded_file = st.file_uploader("📤 Upload CSV file with intern progress (daily data)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Validate columns
    expected_cols = {"Date", "Team ID", "Team Lead", "Intern Name", "Topic", "Status"}
    if not expected_cols.issubset(df.columns):
        st.error(f"CSV missing columns. Required columns: {expected_cols}")
        st.stop()

    # Convert Date column to datetime
    df["Date"] = pd.to_datetime(df["Date"])

    # Topics list from CSV unique topics
    topics = df["Topic"].unique().tolist()
    status_colors = {
        "Not Started": "🔴",
        "Partially Completed": "🟡",
        "Completed": "🟢"
    }

    # Sidebar controls
    view_mode = st.sidebar.radio("📅 View Mode", ["Weekly", "Daily"])

    # Get unique teams in order of appearance
    ordered_teams = df["Team ID"].drop_duplicates().tolist()
    team_selected = st.sidebar.selectbox("📌 Select a Team", ordered_teams)

    team_df = df[df["Team ID"] == team_selected]
    lead = team_df["Team Lead"].iloc[0]
    st.markdown(f"👨‍💼 **Team Lead:** `{lead}`")

    if view_mode == "Daily":
        selected_date = st.sidebar.date_input("Select Date", value=df["Date"].min())
        daily_df = team_df[team_df["Date"] == pd.to_datetime(selected_date)]

        if daily_df.empty:
            st.warning(f"No data for team {team_selected} on {selected_date}")
        else:
            st.markdown(f"### 🔥 Progress Heatmap for {selected_date}")
            # Create heatmap data pivot: Interns as rows, Topics as cols with emoji status
            interns = daily_df["Intern Name"].unique()
            heatmap_rows = []
            for intern in interns:
                row = {"Intern": intern}
                intern_data = daily_df[daily_df["Intern Name"] == intern]
                completed = 0
                for topic in topics:
                    topic_status = intern_data[intern_data["Topic"] == topic]["Status"]
                    if not topic_status.empty:
                        status = topic_status.values[0]
                        emoji = status_colors.get(status, "❓")
                        if emoji == "🟢":
                            completed += 1
                    else:
                        emoji = "❓"
                    row[topic] = emoji
                row["Completion %"] = round((completed / len(topics)) * 100, 2)
                heatmap_rows.append(row)
            emoji_df = pd.DataFrame(heatmap_rows).sort_values(by="Completion %", ascending=False).reset_index(drop=True)
            st.dataframe(emoji_df, use_container_width=True)

            # Bar chart for intern completion %
            st.markdown("### 📊 Intern Completion Percentage")
            bar_fig = px.bar(
                emoji_df,
                x="Intern",
                y="Completion %",
                text="Completion %",
                color="Completion %",
                color_continuous_scale="viridis",
                title=f"Intern Completion Percentage on {selected_date}"
            )
            st.plotly_chart(bar_fig, use_container_width=True)

            # Pie chart for status distribution for the day
            st.markdown("### 🥧 Overall Course Completion Status")
            all_statuses = daily_df["Status"].tolist()
            status_count = pd.Series(all_statuses).value_counts().rename_axis("Status").reset_index(name="Count")
            pie_fig = px.pie(
                status_count,
                names="Status",
                values="Count",
                title=f"Status Distribution on {selected_date}",
                color_discrete_map={
                    "Completed": "#2ecc71",
                    "Partially Completed": "#f1c40f",
                    "Not Started": "#e74c3c"
                }
            )
            st.plotly_chart(pie_fig, use_container_width=True)

    else:  # Weekly View
        # Calculate week number for each date
        df["Week_Number"] = df["Date"].dt.isocalendar().week
        team_df = df[df["Team ID"] == team_selected]

        # List available weeks for team
        available_weeks = sorted(team_df["Week_Number"].unique())
        selected_week = st.sidebar.selectbox("Select Week Number", available_weeks)

        week_df = team_df[team_df["Week_Number"] == selected_week]

        if week_df.empty:
            st.warning(f"No data for team {team_selected} in week {selected_week}")
        else:
            st.markdown(f"### 🔥 Progress Heatmap for Week {selected_week}")

            # Aggregate weekly status by intern & topic: 
            # For simplicity, consider the best status achieved that week:
            # Completed > Partially Completed > Not Started
            status_priority = {"Not Started": 0, "Partially Completed": 1, "Completed": 2}

            # Pivot table to get max status per intern-topic for the week
            pivot_rows = []
            interns = week_df["Intern Name"].unique()

            for intern in interns:
                row = {"Intern": intern}
                intern_data = week_df[week_df["Intern Name"] == intern]
                completed = 0
                for topic in topics:
                    topic_statuses = intern_data[intern_data["Topic"] == topic]["Status"]
                    if not topic_statuses.empty:
                        # Pick status with max priority
                        best_status = max(topic_statuses, key=lambda s: status_priority.get(s, -1))
                        emoji = status_colors.get(best_status, "❓")
                        if emoji == "🟢":
                            completed += 1
                    else:
                        emoji = "❓"
                    row[topic] = emoji
                row["Completion %"] = round((completed / len(topics)) * 100, 2)
                pivot_rows.append(row)

            emoji_df = pd.DataFrame(pivot_rows).sort_values(by="Completion %", ascending=False).reset_index(drop=True)
            st.dataframe(emoji_df, use_container_width=True)

            # Bar chart: intern completion %
            st.markdown("### 📊 Intern Completion Percentage")
            bar_fig = px.bar(
                emoji_df,
                x="Intern",
                y="Completion %",
                text="Completion %",
                color="Completion %",
                color_continuous_scale="viridis",
                title=f"Intern Completion Percentage in Week {selected_week}"
            )
            st.plotly_chart(bar_fig, use_container_width=True)

            # Pie chart: overall status distribution for the week
            st.markdown("### 🥧 Overall Course Completion Status")
            all_statuses = week_df["Status"].tolist()
            status_count = pd.Series(all_statuses).value_counts().rename_axis("Status").reset_index(name="Count")
            pie_fig = px.pie(
                status_count,
                names="Status",
                values="Count",
                title=f"Status Distribution in Week {selected_week}",
                color_discrete_map={
                    "Completed": "#2ecc71",
                    "Partially Completed": "#f1c40f",
                    "Not Started": "#e74c3c"
                }
            )
            st.plotly_chart(pie_fig, use_container_width=True)

            # Team completion ranking table (all teams)
            st.markdown("### 🏆 Team Completion Ranking (All Teams)")
            team_summary = []
            for team_id in df["Team ID"].unique():
                tdf = df[(df["Team ID"] == team_id) & (df["Week_Number"] == selected_week)]
                completed_count = 0
                total_possible = len(tdf) * len(topics)
                for topic in topics:
                    completed_count += tdf[tdf["Status"] == "Completed"].shape[0]
                if total_possible > 0:
                    completion_percent = round((completed_count / total_possible) * 100, 2)
                else:
                    completion_percent = 0.0
                team_summary.append((team_id, completion_percent))
            team_rank_df = pd.DataFrame(team_summary, columns=["Team ID", "Completion %"])
            st.dataframe(team_rank_df.sort_values(by="Completion %", ascending=False).reset_index(drop=True), use_container_width=True)

else:
    st.info("📂 Please upload a CSV file to begin.")

