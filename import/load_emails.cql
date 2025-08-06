// import/load_emails.cql

LOAD CSV WITH HEADERS
  FROM 'file:///Clean_Emails.csv' AS row
  FIELDTERMINATOR ','

// Skip rows without a valid Revision_ID
WITH row
WHERE row.Revision_ID IS NOT NULL AND row.Revision_ID <> ''

// Prep all fields and robustly parse Receiver_ID
WITH
  coalesce(trim(row.Conversation_ID), 'unknown') AS convId,
  row,
  replace(row.Time_Received, ' ', 'T')         AS tsReceived,
  replace(row.Time_Modified, ' ', 'T')         AS tsModified,
  coalesce(row.embedding, '[]')                AS rawEmbedding,
  [x IN split(
      replace(replace(row.Receiver_ID, '[', ''), ']', ''),
      ','
   )
   WHERE trim(x) <> ''
   | replace(trim(x), "'", "")
  ] AS receivers

// Parse embedding as list of floats
WITH
  convId,
  row,
  tsReceived,
  tsModified,
  receivers,
  [ x IN split(substring(rawEmbedding, 2, size(rawEmbedding)-2), ',')
    WHERE trim(x) <> '' AND toFloat(trim(x)) IS NOT NULL
    | toFloat(trim(x))
  ] AS embeddingList

// Merge into the graph
MERGE (c:Conversation { conversationId: convId })

MERGE (e:Email { revisionId: toInteger(row.Revision_ID) })
  SET
    e.emailId        = toInteger(row.Email_ID),
    e.documentId     = toInteger(row.Document_ID),
    e.conversationId = convId,
    e.senderId       = row.Sender_ID,
    e.subject        = row.Email_Subject,
    e.content        = row.Email_Content,
    e.timeReceived   = datetime(tsReceived),
    e.timeModified   = datetime(tsModified),
    e.embedding      = embeddingList

MERGE (e)-[:PART_OF]->(c)
MERGE (s:Person { personId: row.Sender_ID })
MERGE (s)-[:SENT]->(e)

// Create RECEIVED relationships for all receivers, skip blank
FOREACH (rId IN receivers |
  FOREACH (_ IN CASE WHEN rId IS NOT NULL AND rId <> '' THEN [1] ELSE [] END |
    MERGE (r:Person { personId: rId })
    MERGE (r)-[:RECEIVED]->(e)
  )
)

RETURN count(*) AS loaded;
