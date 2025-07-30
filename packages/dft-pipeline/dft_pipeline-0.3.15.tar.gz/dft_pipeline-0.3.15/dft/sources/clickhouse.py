"""ClickHouse data source"""

import pyarrow as pa
from typing import Any, Dict, Optional
import logging

from ..core.base import DataSource
from ..core.data_packet import DataPacket


class ClickHouseSource(DataSource):
    """ClickHouse database data source"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"dft.sources.clickhouse.{self.name}")
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract data from ClickHouse"""
        
        query = self.get_config("query")
        if not query:
            raise ValueError("query is required for ClickHouse source")
        
        try:
            from clickhouse_driver import Client
        except ImportError:
            raise ImportError("clickhouse-driver is required for ClickHouse source. Install with: pip install clickhouse-driver")
        
        # Connection parameters
        host = self.get_config("host", "localhost")
        port = self.get_config("port", 9000)
        database = self.get_config("database", "default")
        user = self.get_config("user", "default")
        password = self.get_config("password", "")
        
        try:
            # Connect to ClickHouse
            client = Client(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
            )
            
            # Execute query and get results with column info
            result = client.execute(query, with_column_types=True)
            data, columns = result
            
            print(f"🔥 DFT v0.3.14 - ClickHouse результат получен:")
            print(f"📊 Количество строк: {len(data) if data else 0}")
            print(f"📋 Колонки: {[col[0] for col in columns] if columns else 'Нет колонок'}")
            
            # Convert to list of dicts
            if columns:
                column_names = [col[0] for col in columns]
                data_list = []
                
                if data:
                    print(f"✅ Есть данные! Обрабатываем {len(data)} строк...")
                    # Has data - convert rows with type conversion
                    for i, row in enumerate(data):
                        row_dict = {}
                        for j, value in enumerate(row):
                            original_value = value
                            # Convert datetime.date to string for PyArrow compatibility
                            if hasattr(value, 'isoformat'):  # datetime.date or datetime.datetime
                                value = value.isoformat()
                            # Convert empty strings to None for better PyArrow handling
                            elif value == '':
                                value = None
                            row_dict[column_names[j]] = value
                            
                            # Показать первые несколько преобразований
                            if i < 3 and j < len(column_names):
                                if original_value != value:
                                    print(f"🔄 Строка {i+1}, колонка '{column_names[j]}': '{original_value}' -> '{value}'")
                        
                        data_list.append(row_dict)
                        
                        # Показать первые несколько строк
                        if i < 3:
                            print(f"📝 Строка {i+1}: {row_dict}")
                    
                    print(f"🏗️  Создаем PyArrow таблицу из {len(data_list)} строк...")
                    
                    # Convert to Arrow table using column-wise approach
                    # This avoids schema inference issues with mixed/null values
                    columns_data = {}
                    for col_name in column_names:
                        col_values = [row[col_name] for row in data_list]
                        columns_data[col_name] = col_values
                        print(f"📊 Колонка '{col_name}': {len(col_values)} значений, типы: {set(type(v).__name__ for v in col_values[:5])}")
                    
                    print("🚀 Вызываем pa.table() с новым подходом (v0.3.14)...")
                    table = pa.table(columns_data)
                    print("✅ PyArrow таблица создана успешно!")
                else:
                    # Empty result but with known schema
                    empty_data = {col_name: [] for col_name in column_names}
                    table = pa.table(empty_data)
            else:
                # No columns info - completely empty result
                table = pa.table({})
            
            # Create data packet
            packet = DataPacket(
                data=table,
                source=f"clickhouse:{host}:{database}",
                metadata={
                    "query": query,
                    "host": host,
                    "database": database,
                    "variables": variables or {},
                    "column_types": {col[0]: col[1] for col in columns} if columns else {},
                }
            )
            
            self.logger.info(f"Extracted {packet.row_count} rows from ClickHouse")
            return packet
            
        except Exception as e:
            self.logger.error(f"Failed to extract from ClickHouse: {e}")
            raise RuntimeError(f"ClickHouse extraction failed: {e}")
    
    def test_connection(self) -> bool:
        """Test ClickHouse connection"""
        try:
            from clickhouse_driver import Client
            
            client = Client(
                host=self.get_config("host", "localhost"),
                port=self.get_config("port", 9000),
                database=self.get_config("database", "default"),
                user=self.get_config("user", "default"),
                password=self.get_config("password", ""),
            )
            
            # Simple test query
            client.execute("SELECT 1")
            return True
            
        except Exception as e:
            self.logger.error(f"ClickHouse connection test failed: {e}")
            return False