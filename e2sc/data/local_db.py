"""Local database access for E2sc."""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from e2sc.utils import get_config, get_logger

logger = get_logger(__name__)


class LocalDatabase:
    """Base class for local database access."""
    
    def __init__(self, db_name: str):
        """Initialize database connection.
        
        Args:
            db_name: Database name (without .db extension)
        """
        self.db_name = db_name
        config = get_config()
        db_path = Path(config.database.db_path).expanduser()
        self.db_file = db_path / f"{db_name}.db"
        
        # Create database directory if not exists
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self) -> None:
        """Connect to database."""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_file))
            self.conn.row_factory = sqlite3.Row
            logger.debug(f"Connected to database: {self.db_file}")
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.debug(f"Closed database: {self.db_file}")
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SQL query and return results.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    
    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """Execute SQL query with multiple parameter sets.
        
        Args:
            query: SQL query
            params_list: List of parameter tuples
        """
        self.connect()
        cursor = self.conn.cursor()
        cursor.executemany(query, params_list)
        self.conn.commit()
    
    def create_from_csv(self, csv_path: Path, table_name: str) -> None:
        """Create database table from CSV file.
        
        Args:
            csv_path: Path to CSV file
            table_name: Name of table to create
        """
        logger.info(f"Creating table {table_name} from {csv_path}")
        df = pd.read_csv(csv_path)
        self.connect()
        df.to_sql(table_name, self.conn, if_exists="replace", index=False)
        self.conn.commit()
        logger.info(f"Created table {table_name} with {len(df)} rows")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def count(self) -> int:
        """Get total row count of all tables in the database."""
        self.connect()
        cursor = self.conn.cursor()
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        total = 0
        for (table_name,) in tables:
            if table_name == 'sqlite_sequence':
                continue
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            total += cursor.fetchone()[0]
        return total


class STRINGDatabase(LocalDatabase):
    """STRING protein-protein interaction database."""
    
    def __init__(self):
        super().__init__("string")
    
    def get_interactions(self, gene: str, min_score: float = 0.4) -> List[Dict[str, Any]]:
        """Get protein interactions for a gene."""
        # Try 'weight' column first (STRING CSV uses 'weight'), fallback to 'score'
        for score_col in ('weight', 'score', 'combined_score'):
            try:
                query = f"""
                SELECT * FROM string_interactions
                WHERE (source_gene = ? OR target_gene = ?)
                AND {score_col} >= ?
                ORDER BY {score_col} DESC
                """
                return self.execute(query, (gene, gene, min_score))
            except Exception:
                continue
        # Last resort: no score filter
        query = """
        SELECT * FROM string_interactions
        WHERE source_gene = ? OR target_gene = ?
        LIMIT 20
        """
        return self.execute(query, (gene, gene))
    
    def get_network(self, genes: List[str], min_score: float = 0.4) -> List[Dict[str, Any]]:
        """Get interaction network for multiple genes.
        
        Args:
            genes: List of gene symbols
            min_score: Minimum interaction score
            
        Returns:
            List of interaction records
        """
        placeholders = ",".join(["?"] * len(genes))
        for score_col in ('weight', 'combined_score', 'score'):
            try:
                query = f"""
        SELECT * FROM string_interactions
        WHERE source_gene IN ({placeholders})
        AND target_gene IN ({placeholders})
        AND {score_col} >= ?
        ORDER BY {score_col} DESC
        """
                params = tuple(genes) + tuple(genes) + (min_score,)
                return self.execute(query, params)
            except Exception:
                continue
        # Last resort: no score filter
        query = f"""
        SELECT * FROM string_interactions
        WHERE source_gene IN ({placeholders})
        AND target_gene IN ({placeholders})
        LIMIT 50
        """
        params = tuple(genes) + tuple(genes)
        return self.execute(query, params)


class HMDBDatabase(LocalDatabase):
    """HMDB gene-metabolite association database."""
    
    def __init__(self):
        super().__init__("hmdb")
    
    def get_metabolites(self, gene: str) -> List[Dict[str, Any]]:
        """Get metabolites associated with a gene.

        Tries both 'gene_name' and case-insensitive UPPER() matching.

        Args:
            gene: Gene symbol

        Returns:
            List of metabolite records, each guaranteed to have a 'metabolite_name' key.
        """
        # Try exact match first, then case-insensitive fallback
        query_exact = "SELECT * FROM hmdb_associations WHERE gene_name = ?"
        rows = self.execute(query_exact, (gene,))
        if not rows:
            query_icase = "SELECT * FROM hmdb_associations WHERE UPPER(gene_name) = UPPER(?)"
            rows = self.execute(query_icase, (gene,))
        # Normalise: ensure 'metabolite_name' key is always present
        for r in rows:
            if 'metabolite_name' not in r:
                r['metabolite_name'] = r.get('metabolite', r.get('name', ''))
        return rows

    def get_genes(self, metabolite_id: str) -> List[Dict[str, Any]]:
        """Get genes associated with a metabolite.
        
        Args:
            metabolite_id: HMDB metabolite name or ID
            
        Returns:
            List of gene records
        """
        query = "SELECT * FROM hmdb_associations WHERE metabolite_name = ? OR metabolite_name LIKE ?"
        return self.execute(query, (metabolite_id, f"%{metabolite_id}%"))


class TRRUSTDatabase(LocalDatabase):
    """TRRUST transcription factor regulatory database."""
    
    def __init__(self):
        super().__init__("trrust")
    
    def get_targets(self, tf: str) -> List[Dict[str, Any]]:
        """Get target genes of a transcription factor.

        The TRRUST CSV uses 'TF' (uppercase) and 'gene' as column names.
        Returns normalised records with additional keys 'tf' and 'target_gene'.
        """
        query = 'SELECT * FROM trrust_regulations WHERE "TF" = ?'
        rows = self.execute(query, (tf,))
        for r in rows:
            r.setdefault("tf", r.get("TF", ""))
            r.setdefault("target_gene", r.get("gene", ""))
        return rows

    def get_regulators(self, gene: str) -> List[Dict[str, Any]]:
        """Get transcription factors regulating a gene.

        The TRRUST CSV uses 'TF' (uppercase) and 'gene' as column names.
        Returns normalised records with additional keys 'tf' and 'target_gene'.
        """
        query = 'SELECT * FROM trrust_regulations WHERE "gene" = ?'
        rows = self.execute(query, (gene,))
        for r in rows:
            r.setdefault("tf", r.get("TF", ""))
            r.setdefault("target_gene", r.get("gene", ""))
        return rows


class GUTMGENEDatabase(LocalDatabase):
    """GUTMGENE gut microbiome-gene association database."""
    
    def __init__(self):
        super().__init__("gutmgene")
    
    def get_microbes(self, gene: str) -> List[Dict[str, Any]]:
        """Get gut microbes associated with a gene.

        Uses case-insensitive matching because the GUTMGENE CSV mixes casing
        (e.g. 'Tnf', 'TNF', 'Il6', 'IL6').  Returns deduplicated records with
        normalised key 'gut_microbiota'.
        """
        # SQLite COLLATE NOCASE only works for ASCII; use UPPER() for broader coverage
        query = '''SELECT DISTINCT "Gut Microbiota", "Alteration", "Condition",
                          "Associative mode", "Description", "PMID", "human/mouse"
                   FROM gutmgene_associations
                   WHERE UPPER("Gene") = UPPER(?)'''
        rows = self.execute(query, (gene,))
        for r in rows:
            r.setdefault("gut_microbiota", r.get("Gut Microbiota", ""))
        return rows

    def get_genes(self, microbe: str) -> List[Dict[str, Any]]:
        """Get genes associated with a gut microbe."""
        query = 'SELECT * FROM gutmgene_associations WHERE "Gut Microbiota" LIKE ?'
        return self.execute(query, (f"%{microbe}%",))


def initialize_databases(data_dir: Path) -> None:
    """Initialize all databases from CSV files.
    
    Args:
        data_dir: Directory containing CSV files
    """
    databases = {
        "string": ("STRING.csv", "string_interactions"),
        "hmdb": ("HMDB.csv", "hmdb_associations"),
        "trrust": ("TRRUST.csv", "trrust_regulations"),
        "gutmgene": ("GUTMGENE.csv", "gutmgene_associations"),
    }
    
    ENCODINGS = {"gutmgene": "gbk"}  # GUTMGENE.csv is GBK-encoded

    for db_name, (csv_file, table_name) in databases.items():
        csv_path = data_dir / csv_file
        if not csv_path.exists():
            logger.warning(f"CSV file not found: {csv_path}")
            continue
        enc = ENCODINGS.get(db_name, "utf-8")
        try:
            import pandas as _pd
            df = _pd.read_csv(csv_path, encoding=enc)
            db = LocalDatabase(db_name)
            db.connect()
            df.to_sql(table_name, db.conn, if_exists="replace", index=False)
            db.conn.commit()
            db.close()
            logger.info(f"Initialized {db_name} database ({len(df)} rows, encoding={enc})")
        except Exception as e:
            logger.error(f"Failed to initialize {db_name}: {e}")
