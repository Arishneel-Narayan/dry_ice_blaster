import streamlit as st
import pandas as pd
import time

# --- Function to perform the Cost-Benefit Analysis ---
def perform_cba(
    daily_cleaning_frequency,
    manual_staff_count,
    manual_cleaning_hours_per_session,
    staff_hourly_cost,
    dry_ice_blaster_cost,
    liquid_co2_cost_per_litre,
    liquid_co2_consumption_litre_per_hour,
    blaster_maintenance_annual,
    manual_cleaning_chemicals_per_session,
    manual_cleaning_water_per_session,
    manual_cleaning_waste_disposal_per_session,
    dry_ice_cleaning_time_reduction_percent,
    revenue_per_hour_production,
    blaster_power_consumption_kw,
    electricity_cost_per_kwh,
    machine_lifespan_years
):
    """
    Performs the cost-benefit analysis for dry ice blasting vs. manual cleaning,
    including ROI over machine lifespan and simple payback period.
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
    
    liquid_co2_annual_cost = (
        liquid_co2_consumption_litre_per_hour *
        dry_ice_cleaning_hours_per_session *
        liquid_co2_cost_per_litre *
        annual_cleaning_sessions
    )

    blaster_annual_power_cost = (
        blaster_power_consumption_kw *
        dry_ice_cleaning_hours_per_session * # Assuming power consumption only during active blasting
        electricity_cost_per_kwh *
        annual_cleaning_sessions
    )

    total_dry_ice_annual_operational_cost = (
        dry_ice_annual_labor_cost +
        liquid_co2_annual_cost +
        blaster_maintenance_annual +
        blaster_annual_power_cost
    )

    # --- Benefits Calculation ---
    downtime_saved_per_session_hours = manual_cleaning_hours_per_session - dry_ice_cleaning_hours_per_session
    annual_downtime_saved_hours = downtime_saved_per_session_hours * annual_cleaning_sessions
    annual_revenue_gain_from_uptime = annual_downtime_saved_hours * revenue_per_hour_production

    # --- Cost-Benefit Summary ---
    annual_operational_cost_savings = total_manual_annual_operational_cost - total_dry_ice_annual_operational_cost
    
    net_financial_benefit_year_1 = annual_operational_cost_savings + annual_revenue_gain_from_uptime - dry_ice_blaster_cost
    
    net_financial_benefit_subsequent_years = annual_operational_cost_savings + annual_revenue_gain_from_uptime

    # --- ROI Calculation over Machine Lifespan ---
    total_benefit_over_lifespan = net_financial_benefit_year_1 + (net_financial_benefit_subsequent_years * (machine_lifespan_years - 1))
    
    if machine_lifespan_years <= 0:
        total_benefit_over_lifespan = 0
        
    roi_over_lifespan = (total_benefit_over_lifespan / dry_ice_blaster_cost) * 100 if dry_ice_blaster_cost > 0 else 0

    # --- Simple Payback Period Calculation ---
    payback_period_years = "N/A"
    if net_financial_benefit_subsequent_years > 0:
        initial_investment_to_recover = dry_ice_blaster_cost - (annual_operational_cost_savings + annual_revenue_gain_from_uptime)

        if initial_investment_to_recover <= 0:
            payback_period_years = f"< 1 year (Paid back in Year 1)"
        else:
            payback_period_years_float = initial_investment_to_recover / net_financial_benefit_subsequent_years
            payback_period_years = f"{payback_period_years_float:.2f} years"
    elif net_financial_benefit_subsequent_years <= 0 and dry_ice_blaster_cost > 0:
        payback_period_years = "Never (Negative Annual Benefit)"
    elif dry_ice_blaster_cost == 0:
        payback_period_years = "N/A (No initial cost)"


    # Prepare data for table
    data = {
        "Category": [
            "Initial Capital Expenditure",
            "Annual Labor Costs",
            "Annual Consumable Costs (Chemicals/Liquid CO2)",
            "Annual Water Usage Costs",
            "Annual Waste Disposal Costs",
            "Annual Maintenance & Utilities (Blaster)",
            "Annual Blaster Power Costs",
            "Annual Revenue Gain from Reduced Downtime"
        ],
        "Current Manual Cleaning (Annual FJD)": [
            0,
            manual_annual_labor_cost,
            manual_annual_chemical_cost,
            manual_annual_water_cost,
            manual_annual_waste_disposal_cost,
            0,
            0,
            0
        ],
        "Dry Ice Blasting (Annual FJD)": [
            dry_ice_blaster_cost,
            dry_ice_annual_labor_cost,
            liquid_co2_annual_cost,
            0,
            0,
            blaster_maintenance_annual,
            blaster_annual_power_cost,
            annual_revenue_gain_from_uptime
        ]
    }

    df = pd.DataFrame(data)
    
    return df, annual_operational_cost_savings, net_financial_benefit_year_1, net_financial_benefit_subsequent_years, roi_over_lifespan, payback_period_years

# --- Streamlit App ---
st.set_page_config(layout="wide", page_title="Dry Ice Blasting CBA, ROI & Payback Calculator for BCF")

st.title("🏭 Dry Ice Blasting Cost-Benefit Analysis, ROI & Payback for BCF")
st.subheader("Optimize Conveyor Belt Cleaning Efficiency")

st.write(
    "This calculator helps evaluate the financial benefits, Return on Investment, and Payback Period of acquiring a dry ice blaster "
    "for conveyor belt cleaning at BCF, compared to the current manual process. "
    "Adjust the parameters below to see the impact on profitability and investment metrics!"
)

st.markdown("---")

# --- Input Parameters ---
st.header("Input Parameters")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Information from Dry Ice Blaster Supplier")
    dry_ice_blaster_cost = st.number_input(
        "Dry Ice Blaster Purchase Cost (FJD):", min_value=1000.0, value=15000.00, step=1000.00, format="%.2f",
        help="Upfront capital cost of purchasing a dry ice blaster."
    )
    liquid_co2_consumption_litre_per_hour = st.number_input(
        "Liquid CO2 Consumption per Blasting Hour (Litres):", min_value=5.0, value=20.0, step=1.0, format="%.1f",
        help="Estimated litres of liquid CO2 consumed per hour of blasting."
    )
    blaster_power_consumption_kw = st.number_input(
        "Blaster Power Consumption (kW):", min_value=0.1, value=3.0, step=0.1, format="%.1f",
        help="Average electrical power consumption of the dry ice blaster in kilowatts (kW) when operating. Check manufacturer specs."
    )
    dry_ice_cleaning_time_reduction_percent = st.slider(
        "Cleaning Time Reduction with Dry Ice Blasting (%)", min_value=0, max_value=90, value=60, step=5,
        help="Percentage reduction in cleaning time compared to manual method (e.g., 60% reduction means 3 hours becomes 1.2 hours)."
    )
    blaster_maintenance_annual = st.number_input(
        "Annual Dry Ice Blaster Maintenance Cost (FJD):", min_value=0.0, value=500.00, step=100.00, format="%.2f",
        help="Estimated annual cost for maintenance and minor parts."
    )
    machine_lifespan_years = st.number_input(
        "Dry Ice Blaster Estimated Lifespan (Years):", min_value=1, value=5, step=1,
        help="Expected operational life of the dry ice blaster for ROI calculation."
    )

with col2:
    st.subheader("Information from Production & Other Suppliers")
    
    with st.expander("Production & Operations Data", expanded=True):
        daily_cleaning_frequency = st.number_input(
            "Cleaning Sessions per Day:", min_value=1, value=1, step=1,
            help="How many times are conveyor belts cleaned per day?"
        )
        manual_staff_count = st.number_input(
            "Current Staff for Manual Cleaning:", min_value=1, value=3, step=1,
            help="Number of staff currently involved in manual cleaning."
        )
        manual_cleaning_hours_per_session = st.number_input(
            "Manual Cleaning Hours per Session:", min_value=0.5, value=3.0, step=0.5, format="%.1f",
            help="Total hours it takes for the current staff to complete one cleaning session."
        )
        staff_hourly_cost = st.number_input(
            "Average Staff Hourly Cost (FJD):", min_value=0.0, value=6.00, step=0.50, format="%.2f",
            help="Estimated loaded hourly cost per employee (wage + benefits + overhead)."
        )
        revenue_per_hour_production = st.number_input(
            "Estimated Revenue per Hour of Production (FJD):", min_value=0.0, value=500.00, step=50.00, format="%.2f",
            help="Crucial for quantifying the benefit of reduced downtime. Estimate the revenue BCF generates from the production line per hour."
        )

    with st.expander("Manual Cleaning Costs", expanded=True):
        manual_cleaning_chemicals_per_session = st.number_input(
            "Chemicals/Consumables Cost per Session (FJD):", min_value=0.0, value=10.00, step=1.00, format="%.2f",
            help="Estimated cost of brushes, soaps, sanitizers, rags per cleaning session."
        )
        manual_cleaning_water_per_session = st.number_input(
            "Water Usage Cost per Session (FJD):", min_value=0.0, value=5.00, step=0.50, format="%.2f",
            help="Estimated cost of water for washing and rinsing per cleaning session."
        )
        manual_cleaning_waste_disposal_per_session = st.number_input(
            "Waste Disposal Cost per Session (FJD):", min_value=0.0, value=5.00, step=0.50, format="%.2f",
            help="Estimated cost for disposing of contaminated water or rags."
        )

    with st.expander("Utility & Consumable Supplier Costs", expanded=True):
        liquid_co2_cost_per_litre = st.number_input(
            "Liquid CO2 Cost per Litre (FJD):", min_value=0.50, value=5.83, step=0.10, format="%.2f",
            help="Cost of liquid CO2 per litre."
        )
        electricity_cost_per_kwh = st.number_input(
            "Electricity Cost per kWh (FJD):", min_value=0.01, value=0.35, step=0.01, format="%.2f",
            help="Your facility's average electricity cost per kilowatt-hour (kWh). As of June 2025, for commercial users in Fiji, this might be around FJD 0.30 - 0.45, but check your latest FEA bill."
        )


# --- Perform Calculation and Display Results ---
with st.spinner("Updating calculations..."):
    df_cba, annual_operational_cost_savings, net_financial_benefit_year_1, net_financial_benefit_subsequent_years, roi_over_lifespan, payback_period_years = perform_cba(
        daily_cleaning_frequency,
        manual_staff_count,
        manual_cleaning_hours_per_session,
        staff_hourly_cost,
        dry_ice_blaster_cost,
        liquid_co2_cost_per_litre,
        liquid_co2_consumption_litre_per_hour,
        blaster_maintenance_annual,
        manual_cleaning_chemicals_per_session,
        manual_cleaning_water_per_session,
        manual_cleaning_waste_disposal_per_session,
        dry_ice_cleaning_time_reduction_percent,
        revenue_per_hour_production,
        blaster_power_consumption_kw,
        electricity_cost_per_kwh,
        machine_lifespan_years
    )
    
    st.markdown("---")
    st.header("Cost-Benefit Analysis & Investment Metrics")

    st.subheader("Detailed Annual Cost Comparison")
    st.dataframe(df_cba.set_index("Category"))

    st.markdown("---")
    st.subheader("Summary of Financial Impact")

    res_col1, res_col2, res_col3 = st.columns(3)

    with res_col1:
        st.metric(
            label="Annual Operational Cost Savings (Dry Ice vs. Manual)",
            value=f"FJD {annual_operational_cost_savings:,.2f}",
            delta=f"FJD {annual_operational_cost_savings:,.2f}" if annual_operational_cost_savings >= 0 else f"FJD {annual_operational_cost_savings:,.2f}"
        )

    with res_col2:
        st.metric(
            label="Net Financial Benefit - Year 1 (Includes Blaster Purchase)",
            value=f"FJD {net_financial_benefit_year_1:,.2f}",
            delta=f"FJD {net_financial_benefit_year_1:,.2f}" if net_financial_benefit_year_1 >= 0 else f"FJD {net_financial_benefit_year_1:,.2f}"
        )

    with res_col3:
        st.metric(
            label="Net Financial Benefit - Subsequent Years (Annual)",
            value=f"FJD {net_financial_benefit_subsequent_years:,.2f}",
            delta=f"FJD {net_financial_benefit_subsequent_years:,.2f}" if net_financial_benefit_subsequent_years >= 0 else f"FJD {net_financial_benefit_subsequent_years:,.2f}"
        )

    st.markdown("---")
    st.subheader("Investment Metrics")

    col_roi, col_payback = st.columns(2)

    with col_roi:
        st.metric(
            label=f"Return on Investment (ROI) over {machine_lifespan_years} Years",
            value=f"{roi_over_lifespan:,.2f}%",
            delta="Higher is better!" if roi_over_lifespan >= 0 else "Negative ROI"
        )

    with col_payback:
        # Safely determine the delta text
        delta_text = None
        is_positive_payback = False
        try:
            # Check if payback_period_years is a string that contains 'years' and represents a positive number
            if "years" in str(payback_period_years):
                # Extract the numeric part for comparison
                numeric_part_str = str(payback_period_years).split(" ")[0]
                if numeric_part_str != "<": # Handle the "< 1 year" case
                    if float(numeric_part_str) > 0:
                        is_positive_payback = True
        except (ValueError, IndexError):
            is_positive_payback = False # In case of parsing errors

        if is_positive_payback:
            delta_text = "Shorter is better!"

        st.metric(
            label="Simple Payback Period",
            value=f"{payback_period_years}",
            delta=delta_text
        )


    st.markdown("---")
    st.subheader("Key Underlying Assumptions:")
    st.markdown(f"""
    * **Annual Cleaning Sessions:** `Daily Cleaning Frequency * 365 days`
    * **Staff Hourly Cost:** Includes wages, benefits, and general overhead.
    * **Dry Ice Blaster Staff:** Assumed 1 operator for dry ice blasting.
    * **Dry Ice Blaster Power Consumption:** Assumed to be constant during the cleaning session hours.
    * **Electricity Cost per kWh:** Based on BCF's average commercial rate. 
    * **Revenue per Hour of Production:** This is a critical input that significantly impacts the overall benefit. Ensure this value is accurately estimated for BCF.
    * **Return on Investment (ROI) Calculation:** Calculated as `(Total Net Financial Benefit over {machine_lifespan_years} Years / Dry Ice Blaster Purchase Cost) * 100`.
        * **Underlying Assumption:** The annual net financial benefit (operational savings + revenue gain) is assumed to be constant each year after the initial investment year.
    * **Simple Payback Period Calculation:** This calculates the time it takes for the cumulative net benefits to equal the initial investment.
        * **Underlying Assumption:** The annual net financial benefit is assumed to be constant each year. 
    """)

    st.subheader("Qualitative Benefits of Dry Ice Blasting")
    st.markdown("""
    * **Improved Hygiene and Food Safety:** Superior cleaning, crucial for meeting stringent food safety standards (reduced risk of recalls, enhanced brand reputation).
    * **Extended Equipment Lifespan:** Non-abrasive method preserves conveyor belts and associated machinery, reducing long-term capital expenditure.
    * **Enhanced Worker Safety and Morale:** Eliminates chemical exposure, reduces physical strain, and improves working conditions.
    * **Environmental Responsibility:** No secondary waste (water, chemicals), uses recycled CO2, contributing to a smaller environmental footprint.
    * **Consistent Cleaning Quality:** Automated nature ensures a more uniform and deep clean compared to manual variations.
    """)
