from datetime import date, timedelta
from typing import Literal, List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from app.database import get_session
from app.schemas import BalancePoint
from app.services.transaction_service import TransactionService, get_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

from app.models import User
from app.security import get_current_user


@router.get("/foo", response_model=BalancePoint)
def get_foo(
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
        start: date | None = Query(default=None),
        end: date | None = Query(default=None),
        group_by: Literal["day", "week", "month"] = Query(default="day"),
        transaction_service: TransactionService = Depends(get_service),
):
    return BalancePoint()


@router.get("/balance", response_model=List[BalancePoint])
def balance_series(
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
        start: date | None = Query(default=None),
        end: date | None = Query(default=None),
        group_by: Literal["day", "week", "month"] = Query(default="day"),
        transaction_service: TransactionService = Depends(get_service),
) -> List[BalancePoint]:
    session = get_session()
    series: List[BalancePoint] = []
    response: List[BalancePoint] = transaction_service.get_transactions(
        start, end, user, session, group_by
    )
    series.extend(response)
    return series


@router.get("", response_class=HTMLResponse)
def dashboard_page():
    # Simple static HTML that queries /dashboard/balance and draws a chart with Chart.js
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Balance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; padding: 24px; }
      .card { max-width: 900px; margin: 0 auto; padding: 16px 20px; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }
      .row { display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }
      label { font-size: 14px; color: #374151; }
      input, select, button { padding: 8px 10px; border-radius: 8px; border: 1px solid #d1d5db; }
      button { cursor: pointer; }
    </style>
  </head>
  <body>
    <div class="card">
      <h2>Balance Over Time</h2>
      <div class="row">
        <label>Start: <input type="date" id="start" /></label>
        <label>End: <input type="date" id="end" /></label>
        <label>Group by:
          <select id="group_by">
            <option value="day">Day</option>
            <option value="week">Week</option>
            <option value="month">Month</option>
          </select>
        </label>
        <button id="refresh">Refresh</button>
      </div>
      <canvas id="chart" width="900" height="400"></canvas>
    </div>
    <script>
      const ctx = document.getElementById('chart').getContext('2d');
      let chart;
      async function fetchSeries() {
        const start = document.getElementById('start').value;
        const end = document.getElementById('end').value;
        const group_by = document.getElementById('group_by').value;
        const params = new URLSearchParams();
        if (start) params.append('start', start);
        if (end) params.append('end', end);
        if (group_by) params.append('group_by', group_by);
        const res = await fetch(`/dashboard/balance?${params.toString()}`);
        return res.json();
      }
      async function draw() {
        const data = await fetchSeries();
        const labels = data.map(p => p.label);
        const balances = data.map(p => p.balance);
        if (chart) chart.destroy();
        chart = new Chart(ctx, {
          type: 'line',
          data: {
            labels,
            datasets: [{ label: 'Balance', data: balances, tension: 0.25 }]
          },
          options: {
            responsive: true,
            scales: {
              y: { beginAtZero: true }
            }
          }
        });
      }
      document.getElementById('refresh').addEventListener('click', draw);
      draw();
    </script>
  </body>
</html>
"""
