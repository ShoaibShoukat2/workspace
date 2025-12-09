# PDF Generation Module - Complete Guide

## Overview
Automatic PDF generation for estimates, job reports, payout slips, compliance certificates, aur investor reports with professional formatting.

---

## 📄 Key Features

- **Estimate PDFs** - Professional estimate documents with line items
- **Job Report PDFs** - Comprehensive completed job reports
- **Payout Slip PDFs** - Official payout slips for contractors
- **Compliance Certificate PDFs** - Compliance verification certificates
- **Investor Report PDFs** - Detailed investor reports with analytics
- **Professional Formatting** - Clean, branded PDF layouts
- **Automatic Generation** - One-click PDF creation

---

## 📋 Requirements

### Installation
```bash
pip install reportlab>=4.0.0
pip install Pillow>=10.0.0
```

Already added to `requirements.txt`

---

## 📊 Estimate PDF

### 1. Generate Estimate PDF
**Endpoint:** `GET /api/workspace/pdf/estimate/{estimate_id}/`
**Permission:** Admin or FM

**Response:** PDF file download

**PDF Contents:**
- Company header with logo
- Estimate number and date
- Customer information
- Project details
- Line items table with quantities and prices
- Subtotal, tax, discount, and total
- Customer signature (if signed)
- Terms and conditions

**Usage Example:**
```bash
# Download estimate PDF
GET /api/workspace/pdf/estimate/45/

# Response: estimate_EST-000045.pdf
```

**PDF Layout:**
```
┌─────────────────────────────────────────┐
│           ESTIMATE                      │
│                                         │
│  Your Company Name    Estimate #: EST-001│
│  123 Business St      Date: Jan 15, 2024│
│  City, State 12345    Valid Until: Feb 15│
│                                         │
│  BILL TO:                               │
│  John Doe                               │
│  456 Customer Ave                       │
│  Email: john@example.com                │
│                                         │
│  Project: Bathroom Renovation           │
│  Description: Complete bathroom remodel │
│                                         │
│  ┌───┬─────────┬────┬──────┬────────┐  │
│  │ # │ Desc    │ Qty│ Price│ Total  │  │
│  ├───┼─────────┼────┼──────┼────────┤  │
│  │ 1 │ Tiles   │ 50 │$10.00│$500.00 │  │
│  │ 2 │ Labor   │ 20 │$50.00│$1000.00│  │
│  └───┴─────────┴────┴──────┴────────┘  │
│                                         │
│                    Subtotal: $1,500.00  │
│                    Tax (8%): $120.00    │
│                    TOTAL: $1,620.00     │
│                                         │
│  Terms & Conditions: ...                │
└─────────────────────────────────────────┘
```

---

## 📝 Job Report PDF

### 2. Generate Job Report PDF
**Endpoint:** `GET /api/workspace/pdf/job-report/{job_id}/`
**Permission:** Authenticated

**Response:** PDF file download

**PDF Contents:**
- Job information (number, title, status, dates)
- Customer information
- Cost information (estimated vs actual)
- Job description
- Completion details with ratings
- Verification information

**Usage Example:**
```bash
# Download job report PDF
GET /api/workspace/pdf/job-report/123/

# Response: job_report_JOB-000123.pdf
```

**PDF Sections:**
1. **Job Information**
   - Job number, title, status, priority
   - Created, start, due, and completed dates

2. **Customer Information**
   - Name, email, phone, address

3. **Cost Information**
   - Estimated vs actual cost
   - Estimated vs actual hours

4. **Job Description**
   - Detailed work description

5. **Completion Details** (if completed)
   - Submission and verification dates
   - Quality, timeliness, professionalism ratings
   - Overall rating

---

## 💰 Payout Slip PDF

### 3. Generate Payout Slip PDF
**Endpoint:** `GET /api/workspace/pdf/payout-slip/{payout_id}/`
**Permission:** Authenticated

**Response:** PDF file download

**PDF Contents:**
- Payout number and date
- Payment status and method
- Contractor/payee information
- Job information (if applicable)
- Payout amount (highlighted)
- Notes and transaction reference

**Usage Example:**
```bash
# Download payout slip PDF
GET /api/workspace/pdf/payout-slip/45/

# Response: payout_slip_PAY-000045.pdf
```

**PDF Layout:**
```
┌─────────────────────────────────────────┐
│         PAYOUT SLIP                     │
│                                         │
│  Payout Number: PAY-000045              │
│  Date: January 15, 2024                 │
│  Status: COMPLETED                      │
│  Payment Method: Bank Transfer          │
│  Paid Date: January 15, 2024            │
│                                         │
│  Payee Information                      │
│  Contractor: contractor@example.com     │
│  Company: ABC Construction              │
│  License: LIC-12345                     │
│                                         │
│  Job Information                        │
│  Job Number: JOB-000123                 │
│  Job Title: Bathroom Renovation         │
│  Completed: January 10, 2024            │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  PAYOUT AMOUNT: $2,500.00       │   │
│  └─────────────────────────────────┘   │
│                                         │
│  This is an official payout slip.      │
└─────────────────────────────────────────┘
```

---

## 🏆 Compliance Certificate PDF

### 4. Generate Compliance Certificate PDF
**Endpoint:** `GET /api/workspace/pdf/compliance-certificate/{compliance_id}/`
**Permission:** Admin Only

**Response:** PDF file download

**Requirements:**
- Compliance document must be APPROVED status
- Only approved documents can generate certificates

**PDF Contents:**
- Certificate title and number
- Contractor information
- Compliance type and document details
- Issue and expiry dates
- Verification details
- Authorized signature line

**Usage Example:**
```bash
# Download compliance certificate PDF
GET /api/workspace/pdf/compliance-certificate/12/

# Response: compliance_certificate_12.pdf
```

**PDF Layout:**
```
┌─────────────────────────────────────────┐
│    COMPLIANCE CERTIFICATE               │
│    Certificate No: CERT-000012          │
│                                         │
│    This is to certify that              │
│    contractor@example.com               │
│    ABC Construction                     │
│                                         │
│    has successfully completed           │
│    Insurance Certificate                │
│                                         │
│    Document: General Liability          │
│    Document Number: INS-789456          │
│                                         │
│    Valid from 2024-01-01 to 2025-01-01  │
│                                         │
│    Verified By: admin@example.com       │
│    Verification Date: January 15, 2024  │
│    Status: APPROVED                     │
│                                         │
│    ________________________________     │
│    Authorized Signature                 │
│                                         │
│    Generated on January 15, 2024        │
└─────────────────────────────────────────┘
```

---

## 📈 Investor Report PDF

### 5. Generate Investor Report PDF
**Endpoint:** `GET /api/workspace/pdf/investor-report/`
**Permission:** Admin/Investor Only

**Query Parameters:**
- `date_from` - Start date (YYYY-MM-DD) - Default: Last 12 months
- `date_to` - End date (YYYY-MM-DD) - Default: Today

**Response:** PDF file download

**PDF Contents:**
- Report title and period
- Executive summary with key metrics
- Revenue, payouts, profit, ROI
- Job statistics
- Completion rates
- Generation timestamp

**Usage Example:**
```bash
# Download investor report for last 12 months
GET /api/workspace/pdf/investor-report/

# Download investor report for specific period
GET /api/workspace/pdf/investor-report/?date_from=2023-01-01&date_to=2023-12-31

# Response: investor_report_2023-01-01_2023-12-31.pdf
```

**PDF Sections:**
1. **Executive Summary**
   - Total Revenue
   - Total Payouts
   - Net Profit
   - ROI Percentage

2. **Job Statistics**
   - Total Jobs
   - Completed Jobs
   - Active Jobs
   - Pending Jobs
   - Completion Rate

---

## 🎨 PDF Styling

### Color Scheme
- **Primary Blue**: #3498db (Headers, tables)
- **Dark Gray**: #2c3e50 (Text)
- **Green**: #27ae60 (Payout amounts)
- **Purple**: #8e44ad (Investor reports)
- **Light Gray**: #ecf0f1 (Backgrounds)

### Typography
- **Headings**: Helvetica-Bold
- **Body Text**: Helvetica
- **Font Sizes**: 8-26pt depending on element

### Layout
- **Page Size**: Letter (8.5" x 11")
- **Margins**: 1 inch all sides
- **Tables**: Grid borders with alternating row colors
- **Spacing**: Consistent padding and spacing

---

## 🔧 Technical Details

### PDF Library
- **ReportLab**: Professional PDF generation
- **Platypus**: High-level layout engine
- **Table Styling**: Advanced table formatting
- **Paragraph Styling**: Rich text formatting

### File Handling
- **In-Memory Generation**: No temporary files
- **BytesIO Buffer**: Efficient memory usage
- **Direct Download**: Immediate file delivery
- **Proper Headers**: Content-Disposition for downloads

### Performance
- **Fast Generation**: < 1 second for most PDFs
- **Scalable**: Handles large datasets
- **Memory Efficient**: Streaming output

---

## 📊 Use Cases

### Use Case 1: Send Estimate to Customer
```bash
# Generate estimate PDF
GET /api/workspace/pdf/estimate/45/

# Email PDF to customer
# Customer reviews and signs
```

### Use Case 2: Job Completion Documentation
```bash
# Generate job report after completion
GET /api/workspace/pdf/job-report/123/

# Archive for records
# Share with stakeholders
```

### Use Case 3: Contractor Payment
```bash
# Generate payout slip
GET /api/workspace/pdf/payout-slip/45/

# Send to contractor
# Keep for accounting records
```

### Use Case 4: Compliance Verification
```bash
# Generate compliance certificate
GET /api/workspace/pdf/compliance-certificate/12/

# Provide to contractor
# Keep for regulatory compliance
```

### Use Case 5: Investor Reporting
```bash
# Generate quarterly report
GET /api/workspace/pdf/investor-report/?date_from=2024-01-01&date_to=2024-03-31

# Share with investors
# Board meeting documentation
```

---

## 💡 Best Practices

### For Estimates
1. Review estimate before generating PDF
2. Ensure all line items are correct
3. Verify customer information
4. Check tax rates and calculations
5. Include clear terms and conditions

### For Job Reports
1. Complete all job details before generating
2. Ensure completion ratings are entered
3. Add comprehensive job description
4. Verify all dates are accurate

### For Payout Slips
1. Verify payout amount is correct
2. Ensure payment method is specified
3. Add transaction reference if available
4. Include relevant notes

### For Compliance Certificates
1. Only generate for approved documents
2. Verify expiry dates are correct
3. Ensure all verification details are complete
4. Keep digital copies for records

### For Investor Reports
1. Choose appropriate date ranges
2. Review metrics before generating
3. Generate regularly (monthly/quarterly)
4. Archive for historical comparison

---

## 🔒 Security & Permissions

### Access Control
- **Estimate PDF**: Admin or FM only
- **Job Report PDF**: Authenticated users
- **Payout Slip PDF**: Authenticated users (own payouts)
- **Compliance Certificate PDF**: Admin only
- **Investor Report PDF**: Admin/Investor only

### Data Privacy
- Sensitive information protected
- Access logs maintained
- Secure PDF generation
- No data leakage

---

## 🚀 Integration Examples

### Frontend Integration
```javascript
// Download estimate PDF
const downloadEstimatePDF = async (estimateId) => {
  const response = await fetch(
    `/api/workspace/pdf/estimate/${estimateId}/`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `estimate_${estimateId}.pdf`;
  a.click();
};

// Download job report PDF
const downloadJobReportPDF = async (jobId) => {
  const response = await fetch(
    `/api/workspace/pdf/job-report/${jobId}/`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `job_report_${jobId}.pdf`;
  a.click();
};
```

### Email Integration
```python
from django.core.mail import EmailMessage

# Send estimate PDF via email
def send_estimate_email(estimate_id, customer_email):
    # Generate PDF
    pdf_buffer = generate_estimate_pdf(estimate_id)
    
    # Create email
    email = EmailMessage(
        subject=f'Estimate {estimate.estimate_number}',
        body='Please find attached your estimate.',
        from_email='noreply@company.com',
        to=[customer_email]
    )
    
    # Attach PDF
    email.attach(
        f'estimate_{estimate.estimate_number}.pdf',
        pdf_buffer.getvalue(),
        'application/pdf'
    )
    
    # Send
    email.send()
```

---

## 📝 Customization

### Company Branding
Update company information in PDF views:
```python
company_data = [
    ['Your Company Name', ''],
    ['123 Business Street', f'Estimate #: {estimate.estimate_number}'],
    ['City, State 12345', f'Date: {estimate.created_at.strftime("%B %d, %Y")}'],
    ['Phone: (555) 123-4567', f'Valid Until: {estimate.valid_until or "N/A"}'],
]
```

### Logo Integration
Add company logo to PDFs:
```python
from reportlab.platypus import Image

# Add logo
logo = Image('path/to/logo.png', width=2*inch, height=1*inch)
elements.append(logo)
```

### Color Scheme
Customize colors in PDF views:
```python
# Change primary color
colors.HexColor('#YOUR_COLOR')
```

---

## 🎯 Future Enhancements

### Planned Features
- Custom PDF templates per workspace
- Logo upload and branding
- Multi-language support
- Digital signatures
- QR codes for verification
- Watermarks for drafts
- Email integration
- Batch PDF generation
- PDF merging capabilities

---

## 📞 Support

### Common Issues

**Issue: PDF not downloading**
- Check browser settings
- Verify authentication token
- Check network connection

**Issue: Missing data in PDF**
- Ensure all required fields are filled
- Verify data exists in database
- Check permissions

**Issue: Formatting issues**
- Update ReportLab library
- Check PDF viewer compatibility
- Verify font availability

---

## 📚 Additional Resources

### ReportLab Documentation
- https://www.reportlab.com/docs/reportlab-userguide.pdf

### PDF Best Practices
- Use standard fonts for compatibility
- Keep file sizes reasonable
- Test on multiple PDF viewers
- Ensure accessibility compliance

---

**PDF Module Status:** Production Ready
**Last Updated:** December 6, 2024
**Version:** 1.0
**Dependencies:** ReportLab 4.0+, Pillow 10.0+
