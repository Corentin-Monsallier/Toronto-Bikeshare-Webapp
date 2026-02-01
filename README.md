# 🚲 Toronto Bike Share Live Dashboard
A real-time data visualization tool built with **Streamlit** to monitor the availability of Toronto’s Bike Share network. <br>
This application transforms live API data into actionable insights for city commuters.

## Features
* **Interactive Map**: Visualize every station across Toronto with real-time availability markers.
* **Smart Itineraries**: Plan your trip with dedicated routing for both renting and returning bikes.
* **Real-Time Metrics**: Instant tracking of total bikes, mechanical bikes, and e-bikes available.
* **Station Analytics**: Overview of total active stations and available docks across the city.
* **Network Utilization**: Live calculation of system load to visualize current demand.

## 📊 Data Source
This project uses the **Toronto Open Data Portal** to ensure all bike and station counts are accurate and updated in real-time.

## 🌐 Live Application
Check out the live app here: **[toronto-bikeshare-webapp-corentin.streamlit.app](https://toronto-bikeshare-webapp-corentin.streamlit.app/)**

## 🔧 Installation & Setup
To run this project locally, follow these steps:
1. **Clone the repository**:
   ```bash
   git clone [https://github.com/your-username/toronto-bikeshare-webapp.git](https://github.com/your-username/toronto-bikeshare-webapp.git)
   cd toronto-bikeshare-webapp
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
3. **Run the app**:
   ```bash
   streamlit run app.py
