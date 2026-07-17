# Demo Obfuscation & Data Masking Guide
## Securing Sensitive Doctor and Financial Data for Public Presentations

This guide details two methods for obfuscating sensitive clinical and financial records (doctor names, PCodes, spend totals, and territories) for a demo:
1. **Option A: CSS-Based "Demo Mode" Toggle (Recommended)**: Non-destructive, instant, and toggleable in the frontend UI.
2. **Option B: SQL Database-Level Data Masking**: Destructive/Permanent masking directly within your staging and view layer.

---

## Option A: Non-Destructive CSS "Demo Mode" Toggle
This method adds a "Demo Mode" switch to the dashboard header. When active, it applies a CSS blur filter to all HTML elements marked with a `.sensitive` class.

### Step A.1: Define the CSS Blur Utility
Add the following utility rules to your global CSS stylesheet (`frontend/src/index.css` or `App.css`):

```css
/* Base blur styling */
.sensitive-data {
  transition: filter 0.3s ease;
}

/* Apply blur when demo-mode is active */
.demo-mode .sensitive-data {
  filter: blur(5px) !important;
  user-select: none; /* Prevents copying the text from HTML */
  pointer-events: none; /* Prevents hover-based tooltips from revealing values */
}

/* Optional: Slight hover reveal for controlled demoing */
.demo-mode .sensitive-data:hover {
  filter: blur(2px) !important; /* Slightly clearer on direct cursor hover */
}
```

### Step A.2: Create the Global Context / React Hook
Create a state hook in `frontend/src/App.tsx` (or your layout wrapper) to toggle the `.demo-mode` class on the root container:

```tsx
import React, { useState, useEffect } from 'react';

export default function App() {
  const [isDemoMode, setIsDemoMode] = useState(false);

  // Toggle class on the body tag
  useEffect(() => {
    if (isDemoMode) {
      document.body.classList.add('demo-mode');
    } else {
      document.body.classList.remove('demo-mode');
    }
  }, [isDemoMode]);

  return (
    <div className="app-container">
      <header className="flex justify-between items-center p-4 bg-gray-900 text-white">
        <h1>Cipla Execution Intelligence</h1>
        <div className="flex items-center gap-2">
          <label htmlFor="demo-toggle" className="text-sm text-gray-400">Demo Mode (Blur Data)</label>
          <input
            id="demo-toggle"
            type="checkbox"
            checked={isDemoMode}
            onChange={(e) => setIsDemoMode(e.target.checked)}
            className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500"
          />
        </div>
      </header>
      
      {/* Rest of your pages */}
    </div>
  );
}
```

### Step A.3: Mark Sensitive Elements in Components
Add the `sensitive-data` class to any component rendering sensitive properties:

```tsx
// Example Doctor Row Card
<tr>
  <td className="sensitive-data font-mono">{doctor.pcodeNormalized}</td>
  <td className="sensitive-data font-semibold">{doctor.doctorName}</td>
  <td>{doctor.speciality}</td>
  <td className="sensitive-data">{formatCurrency(doctor.totalRoiSpendUsd)}</td>
</tr>
```

---

## Option B: Database-Level Masking (Secure SQL Scripts)
If you are sharing database access with external developers, or hosting a public preview where the network console must not contain real API values, you must mask the database table rows directly.

Run the following SQL script in your Supabase SQL Editor to mask staging tables **before** refreshing your materialized views:

```sql
-- 1. Mask Doctor Names and PCodes in raw Doctors table
UPDATE doctors
SET 
  latest_doctor_name = CONCAT(LEFT(latest_doctor_name, 1), '*** ', RIGHT(latest_doctor_name, 1)),
  pcode_normalized = CONCAT(LEFT(pcode_normalized, 3), '-XXXX');

-- 2. Mask names and PCodes in consolidated request attendance
UPDATE request_doctors
SET 
  doctor_name_raw = CONCAT(LEFT(doctor_name_raw, 1), '*** ', RIGHT(doctor_name_raw, 1)),
  pcode_normalized = CONCAT(LEFT(pcode_normalized, 3), '-XXXX'),
  pcode_raw = CONCAT(LEFT(pcode_raw, 3), '-XXXX')
WHERE pcode_normalized IS NOT NULL;

-- 3. Mask names in contract economics
UPDATE doctor_engagement_facts
SET 
  doctor_name = CONCAT(LEFT(doctor_name, 1), '*** ', RIGHT(doctor_name, 1)),
  pcode_normalized = CONCAT(LEFT(pcode_normalized, 3), '-XXXX');

-- 4. Mask names in RCPA Summaries
UPDATE rcpa_doctor_month_summary
SET 
  doctor_name = CONCAT(LEFT(doctor_name, 1), '*** ', RIGHT(doctor_name, 1)),
  pcode_normalized = CONCAT(LEFT(pcode_normalized, 3), '-XXXX');

-- 5. Add random noise to financial totals to disguise real spending (+/- 15%)
UPDATE execution_requests
SET 
  actual_btu_expense_local = actual_btu_expense_local * (0.85 + random() * 0.30),
  actual_btc_expense_local = actual_btc_expense_local * (0.85 + random() * 0.30),
  actual_total_expense_local = actual_total_expense_local * (0.85 + random() * 0.30),
  actual_total_expense_usd = actual_total_expense_usd * (0.85 + random() * 0.30);

-- 6. Trigger Materialized View Refresh to update the dashboard tables
SELECT refresh_dashboard_materialized_views();
```
*(Warning: This is a destructive operation. Run this on a copy/clone of your database instance, not your primary production dataset).*
