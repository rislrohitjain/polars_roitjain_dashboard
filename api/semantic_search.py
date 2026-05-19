import json
import polars as pl
from typing import List, Literal, Union
from pydantic import BaseModel, Field
from openai import OpenAI

class FilterCondition(BaseModel):
    column: str = Field(description="Exact case-sensitive column name.")
    operator: Literal["eq", "neq", "gt", "lt", "gte", "lte", "contains", "starts_with"] = Field(description="Operator.")
    value: Union[str, int, float, bool] = Field(description="Target filter value.")

class QueryIntent(BaseModel):
    explanation: str = Field(description="Short recap.")
    filters: List[FilterCondition] = Field(default=[])

def run_isolated_semantic_filter(user_query: str, df: pl.DataFrame) -> pl.DataFrame:
    """
    Takes an input DataFrame, applies AI filters locally, and returns a new 
    filtered copy without altering the original memory state of the parent frame.
    """
    if not user_query.strip():
        return df
        
    try:
        client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        schema_info = {col: str(dtype) for col, dtype in df.schema.items()}
        
        system_prompt = f"""
        Map this natural language request to structural filters.
        Columns: {json.dumps(schema_info)}
        """
        
        response = client.beta.chat.completions.parse(
            model="llama3", # or your preferred local model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            response_format=QueryIntent,
            temperature=0.0
        )
        
        intent = response.choices[0].message.parsed
        expressions = []
        
        for cond in intent.filters:
            if cond.column not in df.columns:
                continue
            expr = pl.col(cond.column)
            if cond.operator == "eq": expressions.append(expr == cond.value)
            elif cond.operator == "neq": expressions.append(expr != cond.value)
            elif cond.operator == "gt": expressions.append(expr > cond.value)
            elif cond.operator == "gte": expressions.append(expr >= cond.value)
            elif cond.operator == "lt": expressions.append(expr < cond.value)
            elif cond.operator == "lte": expressions.append(expr <= cond.value)
            elif cond.operator == "contains": expressions.append(expr.str.contains(str(cond.value), literal=True))
            elif cond.operator == "starts_with": expressions.append(expr.str.starts_with(str(cond.value)))
            
        return df.filter(expressions) if expressions else df
    except Exception:
        # Fallback gracefully to return original dataframe untouched if AI engine is offline
        return df