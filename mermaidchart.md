```mermaid

sequenceDiagram
    participant Binance API
    participant API
    participant Model(s)
    participant Google Big Query
    participant Frontend (Heroku / Streamlit)
    Binance API->>API: Cleaned data ready for export
    API ->> Model(s): 
    Model(s)->>Google Big Query: 
    Google Big Query->>Frontend (Heroku / Streamlit): 
    
```