# stephanie/db/orm/score_dimension.py
from sqlalchemy import JSON, Column, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ScoreDimensionORM(Base):
    __tablename__ = "score_dimensions"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # e.g., 'clarity'
    stage = Column(String, nullable=True)               # e.g., 'review', 'reflection'
    prompt_template = Column(Text, nullable=False)      # Template with {goal}, {hypothesis}, etc.
    weight = Column(Float, default=1.0)

    # Optional relationships or metadata fields
    notes = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Flexible config extension

    # def to_score_dimension(self, parser_fn):
    #     from mrq.scoring import ScoreDimension
    #     return ScoreDimension(
    #         name=self.name,
    #         prompt_template=self.prompt_template,
    #         weight=self.weight,
    #         parser=parser_fn,
    #     )
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "stage": self.stage,
            "prompt_template": self.prompt_template,
            "weight": self.weight,
            "notes": self.notes,
            "extra_data": self.extra_data or {},
        }
    