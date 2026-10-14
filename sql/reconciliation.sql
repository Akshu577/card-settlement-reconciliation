-- Reconciliation: classify every approved switch transaction against the network settlement file.
-- name: recon_summary
WITH settle AS (
    SELECT txn_id, COUNT(*) AS n_records, SUM(settled_amount) AS settled_total, MAX(settled_amount) AS settled_amount
    FROM network_settlement
    GROUP BY txn_id
),
classified AS (
    SELECT
        s.txn_id,
        s.amount,
        CASE
            WHEN n.txn_id IS NULL THEN 'Missing in settlement'
            WHEN n.n_records > 1 THEN 'Duplicate settlement'
            WHEN ABS(n.settled_amount - s.amount) > 0.01 THEN 'Amount mismatch'
            ELSE 'Matched'
        END AS recon_status,
        COALESCE(n.settled_total, 0) - s.amount AS variance
    FROM switch_transactions s
    LEFT JOIN settle n ON n.txn_id = s.txn_id
    WHERE s.status = 'APPROVED'
)
SELECT recon_status,
       COUNT(*) AS transactions,
       ROUND(SUM(amount), 2) AS switch_amount,
       ROUND(SUM(variance), 2) AS net_variance
FROM classified
GROUP BY recon_status
ORDER BY transactions DESC;

-- name: orphan_settlements
-- Settled by the network with no matching switch transaction: possible fraud, or a switch logging gap.
SELECT COUNT(*) AS orphan_records, ROUND(SUM(settled_amount), 2) AS orphan_amount
FROM network_settlement n
WHERE NOT EXISTS (SELECT 1 FROM switch_transactions s WHERE s.txn_id = n.txn_id);

-- name: exceptions_by_channel
-- Where do breaks come from? Exception rate by channel.
WITH settle AS (
    SELECT txn_id, COUNT(*) AS n_records, MAX(settled_amount) AS settled_amount
    FROM network_settlement GROUP BY txn_id
)
SELECT s.channel,
       COUNT(*) AS approved_txns,
       SUM(CASE WHEN n.txn_id IS NULL OR n.n_records > 1
                  OR ABS(n.settled_amount - s.amount) > 0.01 THEN 1 ELSE 0 END) AS exceptions,
       ROUND(100.0 * SUM(CASE WHEN n.txn_id IS NULL OR n.n_records > 1
                  OR ABS(n.settled_amount - s.amount) > 0.01 THEN 1 ELSE 0 END) / COUNT(*), 2) AS exception_rate_pct
FROM switch_transactions s
LEFT JOIN settle n ON n.txn_id = s.txn_id
WHERE s.status = 'APPROVED'
GROUP BY s.channel
ORDER BY exception_rate_pct DESC;
