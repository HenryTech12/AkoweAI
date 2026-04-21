"""Financial report generation task."""
import logging
import asyncio
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from model.database import SessionLocal
from db.crud import (
    update_report, get_user_transactions, get_transaction_statistics
)
from service.claude_service import generate_financial_insights
from service.cloudinary_service import upload_file
import json

logger = logging.getLogger(__name__)


def generate_report(user_id: str, report_type: str, start_date: str, end_date: str):
    """
    Generate financial report:
    1. Fetch user transactions
    2. Calculate statistics
    3. Generate insights
    4. Create PDF
    5. Upload to Cloudinary
    """
    db: Session = SessionLocal()

    try:
        user_id_uuid = UUID(user_id)
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Fetch transactions for the period
        transactions, total = get_user_transactions(
            db,
            user_id_uuid,
            start_date=start_dt,
            end_date=end_dt,
            limit=1000
        )

        # Calculate statistics
        stats = get_transaction_statistics(db, user_id_uuid, period_days=30)

        # Prepare transaction data for insights
        transactions_data = [
            {
                "id": str(t.id),
                "amount": float(t.amount),
                "currency": t.currency,
                "category": t.category,
                "description": t.description,
                "date": t.transaction_date.isoformat()
            }
            for t in transactions
        ]

        # Generate insights using Claude (run async function)
        insights = asyncio.run(generate_financial_insights(transactions_data))

        # Calculate credit score estimate
        credit_score = insights.get("credit_score_estimate", 50)

        # Prepare summary data
        summary_data = {
            "total_transactions": total,
            "total_income": float(stats.get("total_income", 0)),
            "total_expenses": float(stats.get("total_expenses", 0)),
            "total_debts": float(stats.get("total_debts", 0)),
            "net_profit": float(stats.get("net_profit", 0)),
            "credit_score": credit_score,
            "insights": insights,
            "period": {
                "start": start_date,
                "end": end_date
            }
        }

        # Generate PDF
        pdf_bytes = _generate_pdf(summary_data, transactions_data)

        # Upload PDF to Cloudinary
        pdf_filename = f"{report_type}_{datetime.utcnow().timestamp()}.pdf"
        pdf_key = asyncio.run(upload_file(pdf_bytes, pdf_filename, f"reports/{user_id}"))

        # Update report in database
        report_update = {
            "status": "completed",
            "pdf_s3_key": pdf_key,
            "summary_data": summary_data
        }

        logger.info(f"Report generated for user {user_id}: {report_type}")

        return {
            "status": "success",
            "report_type": report_type,
            "pdf_key": pdf_key,
            "summary": summary_data
        }

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise

    finally:
        db.close()
    """
    Generate financial report:
    1. Fetch user transactions
    2. Calculate statistics
    3. Generate insights
    4. Create PDF
    5. Upload to S3
    """
    db: Session = SessionLocal()

    try:
        user_id_uuid = UUID(user_id)
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Fetch transactions for the period
        transactions, total = get_user_transactions(
            db,
            user_id_uuid,
            start_date=start_dt,
            end_date=end_dt,
            limit=1000
        )

        # Calculate statistics
        stats = get_transaction_statistics(db, user_id_uuid, period_days=30)

        # Prepare transaction data for insights
        transactions_data = [
            {
                "id": str(t.id),
                "amount": float(t.amount),
                "currency": t.currency,
                "category": t.category,
                "description": t.description,
                "date": t.transaction_date.isoformat()
            }
            for t in transactions
        ]

        # Generate insights using Claude
        insights = await generate_financial_insights(transactions_data)

        # Calculate credit score estimate
        credit_score = insights.get("credit_score_estimate", 50)

        # Prepare summary data
        summary_data = {
            "total_transactions": total,
            "total_income": float(stats.get("total_income", 0)),
            "total_expenses": float(stats.get("total_expenses", 0)),
            "total_debts": float(stats.get("total_debts", 0)),
            "net_profit": float(stats.get("net_profit", 0)),
            "credit_score": credit_score,
            "insights": insights,
            "period": {
                "start": start_date,
                "end": end_date
            }
        }

        # Generate PDF
        pdf_bytes = _generate_pdf(summary_data, transactions_data)

        # Upload PDF to S3
        pdf_key = f"reports/{user_id}/{report_type}_{datetime.utcnow().timestamp()}.pdf"
        await upload_file(pdf_bytes, f"{report_type}_{datetime.utcnow().timestamp()}.pdf", f"reports/{user_id}")

        # Update report in database
        report_update = {
            "status": "completed",
            "pdf_s3_key": pdf_key,
            "summary_data": summary_data
        }

        from db.crud import update_report as update_report_db
        # This would be called from the API endpoint after this task completes

        logger.info(f"Report generated for user {user_id}: {report_type}")

        return {
            "status": "success",
            "report_type": report_type,
            "pdf_s3_key": pdf_key,
            "summary": summary_data
        }

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise

    finally:
        db.close()


def _generate_pdf(summary_data: dict, transactions_data: list) -> bytes:
    """
    Generate PDF report.

    Args:
        summary_data: Summary statistics
        transactions_data: Transaction details

    Returns:
        PDF file bytes
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors
        from io import BytesIO
        from datetime import datetime

        # Create PDF buffer
        pdf_buffer = BytesIO()

        # Create PDF
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        elements.append(Paragraph("AkoweAI Financial Report", title_style))
        elements.append(Spacer(1, 0.3 * inch))

        # Summary section
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12
        )
        elements.append(Paragraph("Financial Summary", summary_style))

        # Summary table
        summary_table_data = [
            ["Metric", "Value"],
            ["Total Income", f"₦{summary_data.get('total_income', 0):,.2f}"],
            ["Total Expenses", f"₦{summary_data.get('total_expenses', 0):,.2f}"],
            ["Net Profit", f"₦{summary_data.get('net_profit', 0):,.2f}"],
            ["Total Debts", f"₦{summary_data.get('total_debts', 0):,.2f}"],
            ["Credit Score", str(summary_data.get('credit_score', 0))],
        ]

        summary_table = Table(summary_table_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Insights section
        elements.append(Paragraph("Financial Insights", summary_style))
        insights = summary_data.get('insights', {})
        insights_text = insights.get('summary', 'No insights available.')
        elements.append(Paragraph(insights_text, styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))

        # Recommendations
        elements.append(Paragraph("Recommendations", summary_style))
        recommendations = insights.get('recommendations', [])
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", styles['Normal']))

        # Add page break if there are many transactions
        if len(transactions_data) > 10:
            elements.append(PageBreak())

        # Transactions section (if not too many)
        if len(transactions_data) <= 50:
            elements.append(Paragraph("Recent Transactions", summary_style))

            trans_table_data = [["Date", "Category", "Amount", "Description"]]
            for trans in transactions_data[:20]:  # Show only first 20
                trans_table_data.append([
                    trans.get('date', '')[:10],
                    trans.get('category', ''),
                    f"₦{trans.get('amount', 0):,.2f}",
                    trans.get('description', '')[:30]
                ])

            trans_table = Table(trans_table_data, colWidths=[1*inch, 1.2*inch, 1.2*inch, 1.6*inch])
            trans_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(trans_table)

        # Build PDF
        doc.build(elements)

        # Get PDF bytes
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.getvalue()

        logger.info(f"PDF generated: {len(pdf_bytes)} bytes")
        return pdf_bytes

    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise
