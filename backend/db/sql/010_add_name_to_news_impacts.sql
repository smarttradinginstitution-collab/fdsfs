-- Aggiunge la colonna 'name' alla tabella 'news_impacts' per memorizzare il nome dell'impatto della notizia.
ALTER TABLE public.news_impacts ADD COLUMN name VARCHAR(255);