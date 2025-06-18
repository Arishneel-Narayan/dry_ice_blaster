import streamlit as st
import pandas as pd

# --- Function to perform the Cost-Benefit Analysis ---
def perform_cba(
    daily_cleaning_frequency,
    manual_staff_count,
    manual_cleaning_hours_per_session,
    staff_hourly_cost,
    dry_ice_blaster_cost,
    dry_ice_cost_per_kg,
    dry_ice_consumption_kg_per_hour,
    blaster_maintenance_annual,
    manual_cleaning_chemicals_per_session,
    manual_cleaning_water_per_session,
    manual_cleaning_waste_disposal_per_session,
    dry_ice_cleaning_time_reduction_percent,
    revenue_per_hour_production,
    blaster_power_consumption_kw, # New Input: Power consumption
    electricity_cost_per_kwh # New Input: Electricity cost
):
    """
    Performs the cost-benefit analysis for dry ice blasting vs. manual cleaning.
    """

    # --- Assumptions (Internal to the function for calculation) ---
    annual_cleaning_sessions = daily_cleaning_frequency * 365 # Assuming daily operation

    # --- Current Manual Cleaning Calculations ---
    manual_man_hours_per_session = manual_staff_count * manual_cleaning_hours_per_session
    manual_annual_labor_cost = manual_man_hours_per_session * staff_hourly_cost * annual_cleaning_sessions
    manual_annual_chemical_cost = manual_cleaning_chemicals_per_session * annual_cleaning_sessions
    manual_annual_water_cost = manual_cleaning_water_per_session * annual_cleaning_sessions
    manual_annual_waste_disposal_cost = manual_cleaning_waste_disposal_per_session * annual_cleaning_sessions
    total_manual_annual_operational_cost = (
        manual_annual_labor_cost +
        manual_annual_chemical_cost +
        manual_annual_water_cost +
        manual_annual_waste_disposal_cost
    )

    # --- Dry Ice Blasting Calculations ---
    dry_ice_cleaning_hours_per_session = manual_cleaning_hours_per_session * (1 - dry_ice_cleaning_time_reduction_percent / 100)
    dry_ice_man_hours_per_session = 1 * dry_ice_cleaning_hours_per_session # Assuming 1 operator for dry ice blasting
    dry_ice_annual_labor_cost = dry_ice_man_hours_per_session * staff_hourly_cost * annual_cleaning_sessions
    
    dry_ice_annual_pellet_cost = (
        dry_ice_consumption_kg_per_hour *
        dry_ice_cleaning_hours_per_session *
        dry_ice_cost_per_kg *
        annual_cleaning_sessions
    )

    # New Calculation: Annual Power Cost for Blaster
    blaster_annual_power_cost = (
        blaster_power_consumption_kw *
        dry_ice_cleaning_hours_per_session * # Assuming power consumption only during active blasting
        electricity_cost_per_kwh *
        annual_cleaning_sessions
    )

    total_dry_ice_annual_operational_cost = (
        dry_ice_annual_labor_cost +
        dry_ice_annual_pellet_cost +
        blaster_maintenance_annual +
        blaster_annual_power_cost # Added power cost
    )

    # --- Benefits Calculation ---
    downtime_saved_per_session_hours = manual_cleaning_hours_per_session - dry_ice_cleaning_hours_per_session
    annual_downtime_saved_hours = downtime_saved_per_session_hours * annual_cleaning_sessions
    annual_revenue_gain_from_uptime = annual_downtime_saved_hours * revenue_per_hour_production

    # --- Cost-Benefit Summary ---
    annual_operational_cost_savings = total_manual_annual_operational_cost - total_dry_ice_annual_operational_cost
    net_financial_benefit_year_1 = annual_operational_cost_savings + annual_revenue_gain_from_uptime - dry_ice_blaster_cost
    net_financial_benefit_subsequent_years = annual_operational_cost_savings + annual_revenue_gain_from_uptime

    # ROI Calculation (using Net Financial Benefit - Subsequent Years for annual return)
    # Underlying Assumption: ROI is calculated as the annual benefit from subsequent years relative to the initial investment.
    # This assumes the 'benefit' is consistent annually after the first year.
    roi_percentage = (net_financial_benefit_subsequent_years / dry_ice_blaster_cost) * 100 if dry_ice_blaster_cost > 0 else 0

    # Prepare data for table
    data = {
        "Category": [
            "Initial Capital Expenditure",
            "Annual Labor Costs",
            "Annual Consumable Costs (Chemicals/Dry Ice)",
            "Annual Water Usage Costs",
            "Annual Waste Disposal Costs",
            "Annual Maintenance & Utilities (Blaster)",
            "Annual Blaster Power Costs", # New row
            "Annual Revenue Gain from Reduced Downtime"
        ],
        "Current Manual Cleaning (Annual FJD)": [
            0,
            manual_annual_labor_cost,
            manual_annual_chemical_cost,
            manual_annual_water_cost,
            manual_annual_waste_disposal_cost,
            0,
            0, # No power cost for manual in this context
            0
        ],
        "Dry Ice Blasting (Annual FJD)": [
            dry_ice_blaster_cost, # Only for Year 1, will be 0 in subsequent years in a detailed model
            dry_ice_annual_labor_cost,
            dry_ice_annual_pellet_cost,
            0, # No water for dry ice blasting
            0, # No secondary waste for dry ice blasting
            blaster_maintenance_annual,
            blaster_annual_power_cost, # Added power cost
            annual_revenue_gain_from_uptime
        ]
    }

    df = pd.DataFrame(data)
    
    return df, annual_operational_cost_savings, net_financial_benefit_year_1, net_financial_benefit_subsequent_years, roi_percentage

# --- Streamlit App ---
st.set_page_config(layout="wide", page_title="Dry Ice Blasting CBA & ROI Calculator for BCF")

st.title("🏭 Dry Ice Blasting Cost-Benefit Analysis & ROI for BCF")
st.subheader("Optimize Conveyor Belt Cleaning Efficiency")

st.write(
    "This calculator helps evaluate the financial benefits and Return on Investment of acquiring a dry ice blaster "
    "for conveyor belt cleaning at BCF, compared to the current manual process. "
    "Adjust the parameters in the sidebar to see the impact on profitability and ROI!"
)

st.markdown("---")

# --- Sidebar for Input Parameters ---
st.sidebar.header("Input Parameters")

st.sidebar.subheader("General Assumptions")
daily_cleaning_frequency = st.sidebar.number_input(
    "Cleaning Sessions per Day:", min_value=1, value=1, step=1,
    help="How many times are conveyor belts cleaned per day?"
)
staff_hourly_cost = st.sidebar.number_input(
    "Average Staff Hourly Cost (FJD):", min_value=0.0, value=6.00, step=0.50, format="%.2f",
    help="Estimated loaded hourly cost per employee (wage + benefits + overhead)."
)
revenue_per_hour_production = st.sidebar.number_input(
    "Estimated Revenue per Hour of Production (FJD):", min_value=0.0, value=500.00, step=50.00, format="%.2f",
    help="Crucial for quantifying the benefit of reduced downtime. Estimate the revenue BCF generates from the production line per hour."
)

st.sidebar.subheader("Current Manual Cleaning Parameters")
manual_staff_count = st.sidebar.number_input(
    "Current Staff for Manual Cleaning:", min_value=1, value=3, step=1,
    help="Number of staff currently involved in manual cleaning."
)
manual_cleaning_hours_per_session = st.sidebar.number_input(
    "Manual Cleaning Hours per Session:", min_value=0.5, value=3.0, step=0.5, format="%.1f",
    help="Total hours it takes for the current staff to complete one cleaning session."
)
manual_cleaning_chemicals_per_session = st.sidebar.number_input(
    "Manual Cleaning Chemicals/Consumables Cost per Session (FJD):", min_value=0.0, value=10.00, step=1.00, format="%.2f",
    help="Estimated cost of brushes, soaps, sanitizers, rags per cleaning session."
)
manual_cleaning_water_per_session = st.sidebar.number_input(
    "Manual Cleaning Water Usage Cost per Session (FJD):", min_value=0.0, value=5.00, step=0.50, format="%.2f",
    help="Estimated cost of water for washing and rinsing per cleaning session."
)
manual_cleaning_waste_disposal_per_session = st.sidebar.number_input(
    "Manual Cleaning Waste Disposal Cost per Session (FJD):", min_value=0.0, value=5.00, step=0.50, format="%.2f",
    help="Estimated cost for disposing of contaminated water or rags."
)

st.sidebar.subheader("Dry Ice Blasting Parameters")
dry_ice_blaster_cost = st.sidebar.number_input(
    "Dry Ice Blaster Purchase Cost (FJD):", min_value=1000.0, value=15000.00, step=1000.00, format="%.2f",
    help="Upfront capital cost of purchasing a dry ice blaster."
)
dry_ice_cost_per_kg = st.sidebar.number_input(
    "Dry Ice Pellets Cost per kg (FJD):", min_value=0.50, value=2.50, step=0.10, format="%.2f",
    help="Cost of dry ice pellets per kilogram."
)
dry_ice_consumption_kg_per_hour = st.sidebar.number_input(
    "Dry Ice Consumption per Blasting Hour (kg):", min_value=5.0, value=20.0, step=1.0, format="%.1f",
    help="Estimated kilograms of dry ice consumed per hour of blasting."
)
blaster_maintenance_annual = st.sidebar.number_input(
    "Annual Dry Ice Blaster Maintenance Cost (FJD):", min_value=0.0, value=500.00, step=100.00, format="%.2f",
    help="Estimated annual cost for maintenance and minor parts."
)
dry_ice_cleaning_time_reduction_percent = st.sidebar.slider(
    "Cleaning Time Reduction with Dry Ice Blasting (%)", min_value=0, max_value=90, value=60, step=5,
    help="Percentage reduction in cleaning time compared to manual method (e.g., 60% reduction means 3 hours becomes 1.2 hours)."
)
st.sidebar.subheader("Dry Ice Blaster Utilities")
blaster_power_consumption_kw = st.sidebar.number_input(
    "Blaster Power Consumption (kW):", min_value=0.1, value=3.0, step=0.1, format="%.1f",
    help="Average electrical power consumption of the dry ice blaster in kilowatts (kW) when operating. Check manufacturer specs."
)
electricity_cost_per_kwh = st.sidebar.number_input(
    "Electricity Cost per kWh (FJD):", min_value=0.01, value=0.35, step=0.01, format="%.2f",
    help="Your facility's average electricity cost per kilowatt-hour (kWh). As of June 2025, for commercial users in Fiji, this might be around FJD 0.30 - 0.45, but check your latest FEA bill."
)


# --- Perform Calculation and Display Results ---
st.header("Cost-Benefit Analysis & ROI Results")

df_cba, annual_operational_cost_savings, net_financial_benefit_year_1, net_financial_benefit_subsequent_years, roi_percentage = perform_cba(
    daily_cleaning_frequency,
    manual_staff_count,
    manual_cleaning_hours_per_session,
    staff_hourly_cost,
    dry_ice_blaster_cost,
    dry_ice_cost_per_kg,
    dry_ice_consumption_kg_per_hour,
    blaster_maintenance_annual,
    manual_cleaning_chemicals_per_session,
    manual_cleaning_water_per_session,
    manual_cleaning_waste_disposal_per_session,
    dry_ice_cleaning_time_reduction_percent,
    revenue_per_hour_production,
    blaster_power_consumption_kw,
    electricity_cost_per_kwh
)

st.write("---")
st.subheader("Detailed Annual Cost Comparison")
st.dataframe(df_cba.set_index("Category"))

st.write("---")
st.subheader("Summary of Financial Impact")

col1, col2, col3, col4 = st.columns(4) # Added one more column for ROI

with col1:
    st.metric(
        label="Annual Operational Cost Savings (Dry Ice vs. Manual)",
        value=f"FJD {annual_operational_cost_savings:,.2f}",
        delta=f"FJD {annual_operational_cost_savings:,.2f}" if annual_operational_cost_savings >= 0 else f"FJD {annual_operational_cost_savings:,.2f}"
    )

with col2:
    st.metric(
        label="Net Financial Benefit - Year 1 (Includes Blaster Purchase)",
        value=f"FJD {net_financial_benefit_year_1:,.2f}",
        delta=f"FJD {net_financial_benefit_year_1:,.2f}" if net_financial_benefit_year_1 >= 0 else f"FJD {net_financial_benefit_year_1:,.2f}"
    )

with col3:
    st.metric(
        label="Net Financial Benefit - Subsequent Years (Annual)",
        value=f"FJD {net_financial_benefit_subsequent_years:,.2f}",
        delta=f"FJD {net_financial_benefit_subsequent_years:,.2f}" if net_financial_benefit_subsequent_years >= 0 else f"FJD {net_financial_benefit_subsequent_years:,.2f}"
    )

with col4: # Display ROI
    st.metric(
        label="Return on Investment (ROI)",
        value=f"{roi_percentage:,.2f}%",
        delta="Higher is better!" if roi_percentage >= 0 else "Negative ROI"
    )

st.write("---")
st.subheader("Key Underlying Assumptions:")
st.markdown("""
* **Annual Cleaning Sessions:** `Daily Cleaning Frequency (set in sidebar) * 365 days`
* **Staff Hourly Cost:** Includes wages, benefits, and general overhead.
* **Dry Ice Blaster Staff:** Assumed 1 operator for dry ice blasting.
* **Dry Ice Blaster Power Consumption:** Assumed to be constant during the cleaning session hours.
* **Electricity Cost per kWh:** Based on your facility's average commercial rate.
* **Dry Ice Blaster Lifespan:** Not explicitly calculated in annual cost, but influences long-term CAPEX planning.
* **Revenue per Hour of Production:** This is a critical input that significantly impacts the overall benefit. Ensure this value is accurately estimated for BCF.
* **Return on Investment (ROI) Calculation:** Calculated as `(Net Financial Benefit - Subsequent Years / Dry Ice Blaster Purchase Cost) * 100`. This provides an annual ROI after the initial investment is absorbed.
""")

st.subheader("Qualitative Benefits of Dry Ice Blasting")
st.markdown("""
* **Improved Hygiene and Food Safety:** Superior cleaning, crucial for meeting stringent food safety standards (reduced risk of recalls, enhanced brand reputation).
* **Extended Equipment Lifespan:** Non-abrasive method preserves conveyor belts and associated machinery, reducing long-term capital expenditure.
* **Enhanced Worker Safety and Morale:** Eliminates chemical exposure, reduces physical strain, and improves working conditions.
* **Environmental Responsibility:** No secondary waste (water, chemicals), uses recycled CO2, contributing to a smaller environmental footprint.
* **Consistent Cleaning Quality:** Automated nature ensures a more uniform and deep clean compared to manual variations.
""")

st.info("Remember: This analysis provides an estimate. Actual values will depend on specific BCF operational data, local supplier quotes, and internal accounting practices.")
