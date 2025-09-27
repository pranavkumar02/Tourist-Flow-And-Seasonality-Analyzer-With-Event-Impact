# Tourist-Flow-And-Seasonality-Analyzer-With-Event-Impact
**Description:**
A data-driven analytics platform that tracks tourist inflows, detects seasonal trends, and measures event/festival impacts across major U.S. destinations.
Our goal is to help tourism boards, hotels, travel agencies, and city planners make data-backed decisions on staffing, marketing, and promotions.

The system integrates multiple reliable U.S. datasets (TSA, NPS, Hotel Occupancy, Event Calendars) and provides interactive dashboards with real-time hotspot/off-season maps.

## Key Features
**Interactive Map (Plotly + Dash):** View current hotspots and off-season destinations.

**Seasonality Insights:** Monthly visitor peaks, off-peak trends, and growth analysis.

**Event Impact Metrics:** Quantify how festivals/events affect tourist inflows.

**Cloud-Based Database:** PostgreSQL hosted on AWS RDS for scalable data handling.

**PostgreSQL + PostGIS:** Geospatial queries and analytics for city/park mapping.

**Business Intelligence Dashboard:** KPIs, trend charts, and actionable insights.

**Business Recommendations:** Insights panel suggesting promotion opportunities and fast-growing destinations.

## Tech Stack
Layer	Technology	Description

**Language:**	Python (Pandas, NumPy, Scikit-learn) Core scripting.

**Data Processing:** Pandas, NumPy	Cleaning, merging, metric computation.

**Visualization:**	Plotly, Dash (interactive charts & maps).

**Database:**	PostgreSQL Relational + geospatial queries.

**Cloud	AWS:** (RDS, S3)	Hosting, storage, compute.

**Infrastructure:** AWS ( S3 for raw data).

**Version Control:**	GitHub	Collaboration, issues, PRs.


## Frontend (and Fullstack UI)

The frontend is a Dash app featuring:

**Views Included:** 

**Home Page (Interactive Map):** Choropleth map of U.S. destinations color-coded by lift % (Hotspot, Normal, Off-Season).

**Filters:** Month, region, destination type, event category.

**Seasonality Heatmaps:** High vs. low tourist months.

**Drilldown View:** Destination-specific time series, seasonality heatmap, event impact cards.

 **Event Impact Panel:** Spikes during festivals/events.  
 
**Events Page:** Event list/calendar with links to affected destinations.

 **Event Impact Panel:** Spikes during festivals/events.   Last update timestamps, missing data alerts.


## Backend & Infrastructure

**ETL Layer:** Python scripts running as ECS Tasks or Lambda jobs.

**Database:** AWS RDS PostgreSQL (with PostGIS).

**Storage:** AWS S3 buckets for raw, cleaned, and mart data.

**Deployment:** dashboard, GitHub Actions.


## Project Status

In Progress (Data Track - Midterm Phase)

Architecture finalized

Data sources identified ( NPS, TSA, Hotels, Events)

ETL in development

Initial dashboard

Next: PostgreSQL setup and dataset cleaning

Event integration and map drilldowns


## Workload Distribution

**Team Member	Responsibilities**

 **Harika Sunkara:** Data pipeline, PostgreSQL schema, event analytics, EDA.
 
 **Pranav Kumar K:**	Dashboard development (Dash/Plotly), Interactive maps, visualization integration.
 
Both members collaborate on cloud deployment, testing, and final presentation.


## Future Roadmap: Sprints / Phases

**Phase	Week Deliverables**

**Phase 1	(Week 2):**	Final architecture, schema design, seed data.

**Phase 2	(Week 3):**	Dataset collection, load TSA/NPS data into Postgres.

**Phase 3	(Week 4):**	data cleaning + processing.

**Phase 4	(Week 5):**	Integrate event datasets, event impact analytics (EDA + metrics).

**Phase 5	(Week 6):**	Interactive map filters, drilldowns, QA dashboard.

**Phase 6	(Week 7):**	AWS deployment (EC2 + RDS), optimize performance, add documentation.

**Phase 7	(Week 8):**	Testing, Final demo, final report submission, presentation.


## How to Run the Project (Midterm Delivery)

Prerequisites

Python 3.10+

PostgreSQL with PostGIS

AWS credentials (for RDS/S3)


## Business Use Case

Tourism boards businesses often lack real-time visibility into seasonality and event-driven demand spikes. This tool empowers decision-makers to:

Allocate staffing during peak months.

Launch promotions in off-season windows.

Benchmark destinations by growth rate.

Justify investments in infrastructure or marketing.

Evaluate event ROI using impact analysis.

Identify fast-growing destinations for future opportunities.

Strategize marketing campaigns around event-driven spikes.


## Authors & Acknowledgements

**Authors**

Harika Sunkara

Pranav Kumar K

 
 **Acknowledgements**
 
Seidenberg School of Computer Science & Information Systems, Pace University.

Capstone Professor for guidance and feedback.
