# CLI Examples for credit-risk-creditum

This document provides examples of how to use the `credit-risk` command-line interface.

## Installation

First, install the package:

```bash
pip install credit-risk-creditum
```

## Basic Usage

### Check Version

```bash
credit-risk --version
```

### Get Help

```bash
credit-risk --help
credit-risk assess --help
credit-risk stress-test --help
```

## Assessment Examples

### Individual Credit Assessment

#### Basic Assessment
```bash
credit-risk assess --type individual --data '{
  "credit_score": 720,
  "monthly_income": 5000,
  "monthly_debt": 1500,
  "loan_amount": 25000,
  "loan_purpose": "auto"
}'
```

#### Assessment with Economic Data
```bash
credit-risk assess --type individual \
  --data '{"credit_score": 720, "monthly_income": 5000, "monthly_debt": 1500, "loan_amount": 25000, "loan_purpose": "auto"}' \
  --economic-data '{"gdp_growth": 0.02, "unemployment_rate": 0.06, "inflation_rate": 0.03}' \
  --output json
```

#### Assessment from File
```bash
# Create application file
cat > individual_app.json << EOF
{
  "credit_score": 720,
  "monthly_income": 5000,
  "monthly_debt": 1500,
  "loan_amount": 25000,
  "loan_purpose": "home_improvement"
}
EOF

# Run assessment
credit-risk assess --type individual --file individual_app.json --output table
```

### Corporate Credit Assessment

#### Basic Corporate Assessment
```bash
credit-risk assess --type corporate --data '{
  "years_in_business": 5,
  "annual_revenue": 500000,
  "industry": "technology",
  "loan_amount": 100000,
  "loan_purpose": "expansion"
}'
```

#### Corporate Assessment with Different Output Formats
```bash
# Summary output (default)
credit-risk assess --type corporate --file corporate_app.json

# Table output
credit-risk assess --type corporate --file corporate_app.json --output table

# JSON output
credit-risk assess --type corporate --file corporate_app.json --output json
```

## Stress Testing Examples

### Basic Stress Testing

#### Individual Stress Test
```bash
credit-risk stress-test --type individual --data '{
  "credit_score": 720,
  "monthly_income": 5000,
  "monthly_debt": 1500,
  "loan_amount": 25000,
  "loan_purpose": "auto"
}'
```

#### Corporate Stress Test
```bash
credit-risk stress-test --type corporate --data '{
  "years_in_business": 5,
  "annual_revenue": 500000,
  "industry": "technology",
  "loan_amount": 100000,
  "loan_purpose": "expansion"
}' --output table
```

### Specific Scenarios

#### Test Only Recession Scenario
```bash
credit-risk stress-test --type individual \
  --file individual_app.json \
  --scenarios recession \
  --output json
```

#### Test Multiple Specific Scenarios
```bash
credit-risk stress-test --type corporate \
  --file corporate_app.json \
  --scenarios recession market_crash \
  --output table
```

## Scenario Information

### List Available Scenarios
```bash
credit-risk scenarios
```

### List Scenarios in JSON Format
```bash
credit-risk scenarios --output json
```

## Sample Data Files

### Individual Application (individual_app.json)
```json
{
  "credit_score": 720,
  "monthly_income": 5000,
  "monthly_debt": 1500,
  "loan_amount": 25000,
  "loan_purpose": "home_improvement"
}
```

### Corporate Application (corporate_app.json)
```json
{
  "years_in_business": 5,
  "annual_revenue": 500000,
  "industry": "technology",
  "loan_amount": 100000,
  "loan_purpose": "expansion"
}
```

### Economic Data (economic_data.json)
```json
{
  "gdp_growth": 0.025,
  "unemployment_rate": 0.045,
  "inflation_rate": 0.02,
  "interest_rate": 0.035,
  "market_volatility": 0.15,
  "industry_growth": {
    "technology": 0.08,
    "healthcare": 0.05,
    "manufacturing": 0.03,
    "retail": 0.01
  }
}
```

## Advanced Examples

### Batch Processing with Shell Scripts

#### Process Multiple Applications
```bash
#!/bin/bash
# process_applications.sh

applications=(
  "excellent_credit.json"
  "good_credit.json"
  "fair_credit.json"
  "poor_credit.json"
)

echo "Processing individual applications..."
for app in "${applications[@]}"; do
  echo "Processing $app..."
  credit-risk assess --type individual --file "$app" --output summary
  echo ""
done
```

#### Stress Test All Applications
```bash
#!/bin/bash
# stress_test_all.sh

for app_file in *.json; do
  if [[ $app_file == *"individual"* ]]; then
    app_type="individual"
  elif [[ $app_file == *"corporate"* ]]; then
    app_type="corporate"
  else
    continue
  fi
  
  echo "Stress testing $app_file ($app_type)..."
  credit-risk stress-test --type "$app_type" --file "$app_file" --output summary
  echo "---"
done
```

### Integration with Other Tools

#### Save Results to CSV
```bash
# Using jq to extract data
credit-risk assess --type individual --file app.json --output json | \
  jq -r '[.decision, .risk_score, .risk_category, .max_loan_amount] | @csv' >> results.csv
```

#### Monitor Risk Trends
```bash
#!/bin/bash
# monitor_risk.sh

app_file="monitor_app.json"
output_file="risk_trend.log"

while true; do
  timestamp=$(date +"%Y-%m-%d %H:%M:%S")
  result=$(credit-risk assess --type individual --file "$app_file" --output json)
  risk_score=$(echo "$result" | jq -r '.risk_score')
  
  echo "$timestamp,$risk_score" >> "$output_file"
  echo "Risk score at $timestamp: $risk_score"
  
  sleep 3600  # Check every hour
done
```

## Error Handling

### Common Error Cases

#### Invalid JSON Data
```bash
# This will fail with a JSON parsing error
credit-risk assess --type individual --data '{"credit_score": 720, "invalid": }'
```

#### Missing Required Fields
```bash
# This will fail validation
credit-risk assess --type individual --data '{"credit_score": 720}'
```

#### File Not Found
```bash
# This will fail with file not found error
credit-risk assess --type individual --file nonexistent.json
```

## Tips and Best Practices

1. **Use Files for Complex Data**: For applications with many fields, use JSON files instead of command-line data.

2. **Validate JSON**: Use tools like `jq` to validate JSON before passing to credit-risk:
   ```bash
   cat app.json | jq . && credit-risk assess --type individual --file app.json
   ```

3. **Output Formats**: Use `json` output for programmatic processing, `table` for human review, and `summary` for quick checks.

4. **Batch Processing**: For processing many applications, consider using shell scripts or other automation tools.

5. **Error Handling**: Always check exit codes in scripts:
   ```bash
   if credit-risk assess --type individual --file app.json; then
     echo "Assessment successful"
   else
     echo "Assessment failed"
   fi
   ```