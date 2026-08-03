import { Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './components/auth/LoginPage';
import { RequireAuth } from './components/auth/RequireAuth';
import { OfferLanding } from './pages/OfferLanding';
import { Simulation } from './pages/Simulation';
import { AccountSelection } from './pages/AccountSelection';
import { PrecontractualReview } from './pages/PrecontractualReview';
import { ChecksStatus } from './pages/ChecksStatus';
import { ScaSigning } from './pages/ScaSigning';
import { DisbursementConfirmation } from './pages/DisbursementConfirmation';
import { ActiveLoanSummary } from './pages/ActiveLoanSummary';
import { AmortizationSchedule } from './pages/AmortizationSchedule';

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected journey routes */}
      <Route
        path="/offers"
        element={
          <RequireAuth>
            <OfferLanding />
          </RequireAuth>
        }
      />

      <Route
        path="/simulation"
        element={
          <RequireAuth>
            <Simulation />
          </RequireAuth>
        }
      />

      <Route
        path="/accounts"
        element={
          <RequireAuth>
            <AccountSelection />
          </RequireAuth>
        }
      />

      <Route
        path="/documents"
        element={
          <RequireAuth>
            <PrecontractualReview />
          </RequireAuth>
        }
      />

      <Route
        path="/checks"
        element={
          <RequireAuth>
            <ChecksStatus />
          </RequireAuth>
        }
      />

      <Route
        path="/signing"
        element={
          <RequireAuth>
            <ScaSigning />
          </RequireAuth>
        }
      />

      <Route
        path="/confirmation"
        element={
          <RequireAuth>
            <DisbursementConfirmation />
          </RequireAuth>
        }
      />

      <Route
        path="/active-loan"
        element={
          <RequireAuth>
            <ActiveLoanSummary />
          </RequireAuth>
        }
      />

      <Route
        path="/amortization"
        element={
          <RequireAuth>
            <AmortizationSchedule />
          </RequireAuth>
        }
      />

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;
