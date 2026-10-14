-- name: dispute_kpis
-- Volume, resolution time and refund rate by reason; shows which dispute types put the bank's SLA at risk.
SELECT d.reason,
       COUNT(*) AS disputes,
       ROUND(SUM(t.amount), 2) AS disputed_amount,
       ROUND(AVG(JULIANDAY(d.closed_date) - JULIANDAY(d.opened_date)), 1) AS avg_days_to_close,
       SUM(CASE WHEN JULIANDAY(d.closed_date) - JULIANDAY(d.opened_date) > 30 THEN 1 ELSE 0 END) AS closed_over_30_days,
       ROUND(100.0 * SUM(d.outcome = 'Customer refunded') / SUM(d.outcome <> 'OPEN'), 1) AS refund_rate_pct,
       SUM(d.outcome = 'OPEN') AS still_open
FROM disputes d
JOIN switch_transactions t ON t.txn_id = d.txn_id
GROUP BY d.reason
ORDER BY disputes DESC;

-- name: monthly_dispute_trend
SELECT SUBSTR(opened_date, 1, 7) AS month,
       COUNT(*) AS disputes_opened,
       ROUND(AVG(JULIANDAY(closed_date) - JULIANDAY(opened_date)), 1) AS avg_days_to_close
FROM disputes
GROUP BY month
ORDER BY month;

-- name: repeat_dispute_cards
-- Cards with 3+ disputes: candidates for fraud review or customer outreach.
SELECT t.card_id, COUNT(*) AS disputes, ROUND(SUM(t.amount), 2) AS disputed_amount
FROM disputes d
JOIN switch_transactions t ON t.txn_id = d.txn_id
GROUP BY t.card_id
HAVING COUNT(*) >= 3
ORDER BY disputes DESC, disputed_amount DESC;
