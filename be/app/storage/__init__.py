from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Dependency to get a database session
