"""
Anomaly Detection Tools
Identifies unusual billing patterns and compliance issues
Using FunctionTool pattern (official ADK approach)
"""
import pandas as pd
from google.adk.tools import FunctionTool
import sys
import os


def detect_anomalies(file_path: str) -> str:
    """
    Detects anomalies and unusual patterns in legal spend data.
    
    Args:
        file_path: Path to the data file
        
    Returns:
        String summary of detected anomalies
    """
    try:
        # Load data
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        else:
            return "❌ Error: Unsupported file type"
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        anomalies = []
        anomalies.append("=== Anomaly Detection Report ===\n")
        
        anomaly_count = 0
        
        # 1. Partners billing for document review
        if 'timekeeper' in df.columns and 'description' in df.columns:
            partner_keywords = ['partner', 'shareholder', 'principal']
            review_keywords = ['document review', 'doc review', 'review documents']
            
            partner_review = df[
                (df['timekeeper'].str.lower().str.contains('|'.join(partner_keywords), na=False)) &
                (df['description'].str.lower().str.contains('|'.join(review_keywords), na=False))
            ]
            
            if len(partner_review) > 0:
                anomaly_count += len(partner_review)
                anomalies.append(f"🚨 ANOMALY 1: Partners Billing for Document Review")
                anomalies.append(f"   Found: {len(partner_review)} line items")
                anomalies.append(f"   Total Amount: ${partner_review['amount'].sum():,.2f}")
                anomalies.append(f"   Recommendation: Review for appropriateness\n")
        
        # 2. Unusually high hourly rates
        if 'rate' in df.columns:
            rate_threshold = df['rate'].quantile(0.95)
            high_rates = df[df['rate'] > rate_threshold]
            
            if len(high_rates) > 0:
                anomaly_count += len(high_rates)
                anomalies.append(f"🚨 ANOMALY 2: Unusually High Rates")
                anomalies.append(f"   Found: {len(high_rates)} line items above ${rate_threshold:.2f}/hr")
                anomalies.append(f"   Highest Rate: ${df['rate'].max():,.2f}/hr")
                anomalies.append(f"   Recommendation: Verify rate agreements\n")
        
        # 3. Block billing (vague descriptions)
        if 'description' in df.columns:
            short_descriptions = df[df['description'].str.len() < 20]
            
            if len(short_descriptions) > len(df) * 0.1:  # More than 10%
                anomaly_count += len(short_descriptions)
                anomalies.append(f"🚨 ANOMALY 3: Potential Block Billing")
                anomalies.append(f"   Found: {len(short_descriptions)} line items with vague descriptions")
                anomalies.append(f"   Percentage: {len(short_descriptions)/len(df)*100:.1f}%")
                anomalies.append(f"   Recommendation: Request detailed billing\n")
        
        # 4. Outlier amounts (statistical)
        if 'amount' in df.columns:
            Q1 = df['amount'].quantile(0.25)
            Q3 = df['amount'].quantile(0.75)
            IQR = Q3 - Q1
            outlier_threshold = Q3 + (1.5 * IQR)
            
            outliers = df[df['amount'] > outlier_threshold]
            
            if len(outliers) > 0:
                anomaly_count += len(outliers)
                anomalies.append(f"🚨 ANOMALY 4: Statistical Outliers")
                anomalies.append(f"   Found: {len(outliers)} line items above ${outlier_threshold:,.2f}")
                anomalies.append(f"   Total Amount: ${outliers['amount'].sum():,.2f}")
                anomalies.append(f"   Recommendation: Review for accuracy\n")
        
        # 5. Weekend/holiday billing
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['day_of_week'] = df['date'].dt.dayofweek
            weekend_billing = df[df['day_of_week'].isin([5, 6])]  # Saturday, Sunday
            
            if len(weekend_billing) > 0:
                anomaly_count += len(weekend_billing)
                anomalies.append(f"🚨 ANOMALY 5: Weekend Billing")
                anomalies.append(f"   Found: {len(weekend_billing)} line items on weekends")
                anomalies.append(f"   Total Amount: ${weekend_billing['amount'].sum():,.2f}")
                anomalies.append(f"   Recommendation: Verify if emergency work\n")
        
        # Summary
        anomalies.append(f"=== Summary ===")
        anomalies.append(f"Total Anomalies Detected: {anomaly_count}")
        anomalies.append(f"Percentage of Data: {anomaly_count/len(df)*100:.1f}%")
        
        if anomaly_count == 0:
            anomalies.append("\n✅ No significant anomalies detected.")
        else:
            anomalies.append(f"\n⚠️ Recommend human review of flagged items.")
        
        return "\n".join(anomalies)
        
    except Exception as e:
        return f"❌ Error detecting anomalies: {str(e)}"


# Create FunctionTool wrapper
DetectAnomaliesTool = FunctionTool(func=detect_anomalies)


