// import/load_emails.cql

// 1) Load your TSV
LOAD CSV WITH HEADERS
  FROM 'file:///emails_clean.tsv' AS row
  FIELDTERMINATOR '\t'

// 2) Skip rows without a valid Revision_ID
WITH row
WHERE row.Revision_ID IS NOT NULL AND row.Revision_ID <> ''

// 3) Extract and prep all fields
WITH
  coalesce(trim(row.Conversation_ID), 'unknown') AS convId,
  row,
  split(row.Receiver_List, ', ')               AS receivers,
  replace(row.Time_Received, ' ', 'T')         AS tsReceived,
  replace(row.Time_Modified, ' ', 'T')         AS tsModified,
  coalesce(row.embedding, '[]')                AS rawEmbedding

// 4) Build a pure‐float embedding list, dropping any blanks or unparsable items
WITH
  convId,
  row,
  receivers,
  tsReceived,
  tsModified,
  [ x IN split(
        substring(rawEmbedding, 2, size(rawEmbedding)-2),
        ','
    )
    WHERE trim(x) <> '' 
      AND toFloat(trim(x)) IS NOT NULL
    | toFloat(trim(x))
  ] AS embeddingList

// 5) Merge into the graph
MERGE (c:Conversation { id: convId })

MERGE (e:Email { revisionId: toInteger(row.Revision_ID) })
  SET
    e.emailId        = toInteger(row.Email_ID),
    e.documentId     = toInteger(row.Document_ID),
    e.conversationId = convId,
    e.senderName     = row.Sender_Name,
    e.senderAddress  = row.Sender_Address,
    e.subject        = row.Email_Subject,
    e.content        = row.Email_Content,
    e.timeReceived   = datetime(tsReceived),
    e.timeModified   = datetime(tsModified),
    e.embedding      = embeddingList

MERGE (e)-[:PART_OF]->(c)
MERGE (s:Person { email: row.Sender_Address })
MERGE (s)-[:SENT]->(e)

FOREACH (rName IN receivers |
  MERGE (r:Person { email: rName })
  MERGE (r)-[:RECEIVED]->(e)
)

RETURN count(*) AS loaded;
