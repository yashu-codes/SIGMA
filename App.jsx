import { useState, useEffect } from "react";
import sigmaLogin from "./sigma-login.png";
import "./App.css";

const API_URL = "http://127.0.0.1:8001";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [page, setPage] = useState("dashboard");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  const [riskData, setRiskData] = useState([]);
  const [riskLoading, setRiskLoading] = useState(false);
  const [riskError, setRiskError] = useState("");

const [explanation, setExplanation] = useState(null);
const [explanationLoading, setExplanationLoading] = useState(false);
const [explanationError, setExplanationError] = useState("");
const [whatIf, setWhatIf] = useState(null);


const [whatIfLoading, setWhatIfLoading] = useState(false);
const [whatIfError, setWhatIfError] = useState("");

const [complianceData, setComplianceData] = useState(null);
const [complianceLoading, setComplianceLoading] = useState(false);
const [complianceError, setComplianceError] = useState("");

const [operationalData, setOperationalData] = useState(null);
const [operationalLoading, setOperationalLoading] = useState(false);
const [operationalError, setOperationalError] = useState("");

const [sustainabilityData, setSustainabilityData] = useState(null);
const [sustainabilityLoading, setSustainabilityLoading] = useState(false);
const [sustainabilityError, setSustainabilityError] = useState("");
  
const [aiQuestion, setAiQuestion] = useState("");
const [aiAnswer, setAiAnswer] = useState("");
const [aiMessages, setAiMessages] = useState([]);
const [aiLoading, setAiLoading] = useState(false);
const [aiError, setAiError] = useState("");
const [aiMine, setAiMine] = useState("M001");
const [aiOpen, setAiOpen] = useState(true);
const [aiFullScreen, setAiFullScreen] = useState(false);

const [aiConversations, setAiConversations] = useState(() => {
  try {
    const saved = localStorage.getItem("sigma_conversations");
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
});

const [currentConversationId, setCurrentConversationId] = useState(null);
const [showConversations, setShowConversations] = useState(false);

useEffect(() => {
  localStorage.setItem(
    "sigma_conversations",
    JSON.stringify(aiConversations)
  );
}, [aiConversations]);

const handleLogin = (e) => {
    e.preventDefault();

    if (!username.trim() || !password.trim()) {
      setError("Please enter username and password");
      return;
    }

    setError("");
    setLoggedIn(true);
  };

  const openRiskPage = async () => {
    setPage("risk");
    setRiskLoading(true);
    setRiskError("");

    try {
      const response = await fetch(`${API_URL}/risk`);

      if (!response.ok) {
        throw new Error("Risk API request failed");
      }

      const data = await response.json();
      setRiskData(data);
    } catch (error) {
      setRiskError(
        "Unable to connect to the SIGMA risk engine. Make sure the backend is running."
      );
    } finally {
      setRiskLoading(false);
    }
  };

  const getRiskExplanation = async (mineId) => {
    if (explanation?.mine_id === mineId) {
  setExplanation(null);
  setExplanationError("");
  return;
}
  setExplanationLoading(true);
  setExplanationError("");
  setExplanation(null);

  try {
    const response = await fetch(
      `${API_URL}/risk-explanation?mine_id=${mineId}`
    );

    if (!response.ok) {
      throw new Error("Explanation request failed");
    }

    const data = await response.json();

    setExplanation(data);
  } catch (error) {
    setExplanationError(
      "Unable to load AI risk explanation."
    );
  } finally {
    setExplanationLoading(false);
  }
};
const getWhatIf = async (mineId) => {

  // If this mine's What-If result is already open, close it
  if (whatIf?.mine_id === mineId) {
    setWhatIf(null);
    setWhatIfError("");
    return;
  }

  setWhatIfLoading(true);
  setWhatIfLoading(true);
setWhatIfError("");
setWhatIf(null);
  try {
    const response = await fetch(
      `${API_URL}/what-if?mine_id=${mineId}`
    );

    if (!response.ok) {
      throw new Error("What-If request failed");
    }

    const data = await response.json();

    console.log("WHAT-IF RESULT:", data);
    setWhatIf({
  ...data,
  mine_id: mineId
});
  } catch (error) {
  console.error("What-If error:", error);
  setWhatIfError("Unable to load What-If analysis.");
} finally {
  setWhatIfLoading(false);
}
};
const openCompliancePage = async () => {
  setPage("compliance");
  setComplianceLoading(true);
  setComplianceError("");

  try {
    const response = await fetch(`${API_URL}/compliance`);

    if (!response.ok) {
      throw new Error("Compliance request failed");
    }

    const data = await response.json();
    setComplianceData(data);
  } catch (error) {
    console.error("Compliance error:", error);
    setComplianceError("Unable to load compliance data.");
  } finally {
    setComplianceLoading(false);
  }
};

const startNewSIGMAChat = () => {
  setAiMessages([]);
  setAiAnswer("");
  setAiQuestion("");
  setAiError("");
  setCurrentConversationId(null);
  setShowConversations(false);
};

const loadSIGMAConversation = (conversation) => {
  const messages = conversation.messages || [];
  setAiMessages(messages);
  setAiAnswer(
    messages.filter((m) => m.role === "assistant").at(-1)?.content || ""
  );
  setAiMine(conversation.mineId || "M001");
  setCurrentConversationId(conversation.id);
  setAiQuestion("");
  setAiError("");
  setShowConversations(false);
  setAiOpen(true);
};

const deleteSIGMAConversation = (conversationId, event) => {
  event.stopPropagation();
  setAiConversations((prev) => prev.filter((c) => c.id !== conversationId));
  if (currentConversationId === conversationId) {
    startNewSIGMAChat();
  }
};

const askSIGMA = async () => {

  const question = aiQuestion.trim();

  if (!question) {
    return;
  }

  setAiLoading(true);

  try {

    const url =
      `${API_URL}/ai-assistant` +
      `?mine_id=${encodeURIComponent(aiMine)}` +
      `&question=${encodeURIComponent(question)}`;

    const response = await fetch(url, {
      method: "GET",
      cache: "no-store"
    });

    const data = await response.json();

    console.log("SIGMA AI RESPONSE:", data);

    if (!response.ok) {
      throw new Error(
        data?.detail || "AI request failed"
      );
    }

    const answer =
      data.answer ||
      "I couldn't generate a response right now.";

setAiAnswer(answer);

    // ------------------------------------------------------
    // ADD USER MESSAGE
    // ------------------------------------------------------

    const userMessage = {
      role: "user",
      content: question,
      timestamp: new Date().toISOString()
    };

    // ------------------------------------------------------
    // ADD SIGMA RESPONSE
    // ------------------------------------------------------

    const sigmaMessage = {
      role: "assistant",
      content: answer,
      timestamp: new Date().toISOString()
    };

    setAiMessages(prev => [
      ...prev,
      userMessage,
      sigmaMessage
    ]);

    // ------------------------------------------------------
    // CREATE / UPDATE CONVERSATION
    // ------------------------------------------------------

    const conversationId =
      currentConversationId || Date.now().toString();

    if (!currentConversationId) {
      setCurrentConversationId(conversationId);
    }

    setAiConversations(prev => {

      const existing = prev.find(
        c => c.id === conversationId
      );

      if (existing) {

        return prev.map(c =>
          c.id === conversationId
            ? {
                ...c,
                messages: [
                  ...c.messages,
                  userMessage,
                  sigmaMessage
                ],
                updatedAt: new Date().toISOString()
              }
            : c
        );

      }

      return [
        {
          id: conversationId,

          title:
            question.length > 40
              ? question.substring(0, 40) + "..."
              : question,

          mineId: aiMine,

          createdAt: new Date().toISOString(),

          updatedAt: new Date().toISOString(),

          messages: [
            userMessage,
            sigmaMessage
          ]
        },

        ...prev
      ];

    });

    setAiQuestion("");

  } catch (error) {

    console.error("SIGMA AI error:", error);

    setAiMessages(prev => [
      ...prev,
      {
        role: "assistant",
        content:
          "SIGMA is temporarily unable to process this request.",
        timestamp: new Date().toISOString()
      }
    ]);

  } finally {

    setAiLoading(false);

  }
};

const openOperationalPage = async () => {
  setPage("operational");
  setOperationalLoading(true);
  setOperationalError("");

  try {
    const response = await fetch(`${API_URL}/operational`);

    if (!response.ok) {
      throw new Error("Operational request failed");
    }

    const data = await response.json();
    setOperationalData(data);
  } catch (error) {
    console.error("Operational error:", error);
    setOperationalError("Unable to load operational data.");
  } finally {
    setOperationalLoading(false);
  }
};
const openSustainabilityPage = async () => {
  setPage("sustainability");
  setSustainabilityLoading(true);
  setSustainabilityError("");

  try {
    const response = await fetch(`${API_URL}/sustainability`);

    if (!response.ok) {
      throw new Error("Sustainability request failed");
    }

    const data = await response.json();
    setSustainabilityData(data);
  } catch (error) {
    console.error("Sustainability error:", error);
    setSustainabilityError("Unable to load sustainability data.");
  } finally {
    setSustainabilityLoading(false);
  }
};

  /* =========================
     LOGIN
     ========================= */

  if (!loggedIn) {
    return (
      <div className="sigma-screen">

        <img
    src={sigmaLogin}
          alt="SIGMA"
          className="sigma-image"
        />

        <form
          className="real-login-form"
          onSubmit={handleLogin}
        >

          <input
            className="username-hitbox"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            aria-label="Username"
            autoComplete="username"
          />

          <div className="password-wrapper">

            <input
              className="password-hitbox"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              aria-label="Password"
              autoComplete="current-password"
            />

            <button
              type="button"
              className="eye-hitbox"
              onClick={() =>
                setShowPassword(!showPassword)
              }
              aria-label="Show password"
            />

          </div>

          <button
            className="login-hitbox"
            type="submit"
            aria-label="Enter Command Center"
          />

          {error && (
            <div className="login-error">
              {error}
            </div>
          )}

        </form>

      </div>
    );
  }

  /* =========================
     RISK INTELLIGENCE PAGE
     ========================= */

  if (page === "risk") {
    return (
      <div className="risk-page">

        <header className="risk-header">

          <div>
            <div className="risk-logo">
              S.I.G.M.A
            </div>

            <div className="risk-subtitle">
              SMART INTEGRATED GOVERNANCE FOR MINING ASSETS
            </div>
          </div>

          <div className="risk-header-actions">

            <button
              className="back-button"
              onClick={() => setPage("dashboard")}
            >
              ← COMMAND CENTER
            </button>

            <button
              className="logout-button"
              onClick={() => {
                setLoggedIn(false);
                setPage("dashboard");
              }}
            >
              LOGOUT
            </button>

          </div>

        </header>

        <main className="risk-content">

          <div className="risk-title">

            <span>AI RISK ENGINE</span>

            <h1>Risk Intelligence</h1>

            <p>
              Predictive governance risk assessment powered by
              machine learning and live mine data.
            </p>

          </div>

          {riskLoading && (
            <div className="risk-message">
              ANALYZING MINE DATA...
            </div>
          )}

          {riskError && (
            <div className="risk-error">
              {riskError}
            </div>
          )}

          {!riskLoading && !riskError && (
  
            <div className="risk-grid">

              {riskData.map((mine) => (

                <div
                  className={`risk-card ${mine.risk_level?.toLowerCase()}`}
                  key={mine.mine_id}
                >

                  <div className="risk-card-top">

                    <div>
                      <div className="mine-id">
                        {mine.mine_id}
                      </div>

                      <h2>
                        Mine Risk Assessment
                      </h2>
                    </div>

                    <div
                      className={`risk-badge ${mine.risk_level?.toLowerCase()}`}
                    >
                      {mine.risk_level}
                    </div>

                  </div>

                  <div className="confidence-section">

                    <div className="confidence-number">
                      {mine.confidence}%
                    </div>

                    <div className="confidence-label">
                      MODEL CONFIDENCE
                    </div>

                  </div>

                  <div className="risk-factors">

                    <h3>RISK DRIVERS</h3>

                    <div className="factor-grid">

                      <div className="factor">
                        <span>Violations</span>
                        <strong>
                          {mine.risk_factors?.violations ?? 0}
                        </strong>
                      </div>

                      <div className="factor">
                        <span>Overdue Actions</span>
                        <strong>
                          {mine.risk_factors?.overdue_actions ?? 0}
                        </strong>
                      </div>

                      <div className="factor">
                        <span>Inspection Score</span>
                        <strong>
                          {mine.risk_factors?.inspection_score ?? 0}
                        </strong>
                      </div>

                      <div className="factor">
                        <span>Maintenance Delay</span>
                        <strong>
 {mine.risk_factors?.maintenance_delay_days ?? 0}d
                        </strong>
                      </div>

                      <div className="factor">
                        <span>Equipment Failures</span>
                        <strong>
                          {mine.risk_factors?.equipment_failures ?? 0}
                        </strong>
                      </div>

                      <div className="factor">
                        <span>Environmental Issues</span>
                        <strong>
                          {mine.risk_factors?.environmental_issues ?? 0}
                        </strong>
                      </div>

 </div>

<button
  className="explanation-button"
  onClick={() => getRiskExplanation(mine.mine_id)}
>
  WHY IS THIS RISK? →
</button>

<button
  className="whatif-button"
  onClick={() => {
  if (whatIf?.mine_id === mine.mine_id) {
    setWhatIf(null);
  } else {
    getWhatIf(mine.mine_id);
  }
}}
>
  WHAT-IF SIMULATOR →
</button>
{whatIf && whatIf.mine_id === mine.mine_id && (
  <div className="whatif-panel">

    <div className="whatif-title">
      WHAT-IF SIMULATION
    </div>

    <div className="whatif-grid">

      <div className="whatif-card">
       <span>CURRENT GOVERNANCE PRESSURE</span>
        <strong>{whatIf.current?.risk}</strong>
        <small>
          Risk Score: {whatIf.current?.risk_score ?? "--"}/100
        </small>
        <small>
          ML Prediction: {whatIf.current?.ml_risk ?? "--"}
        </small>
      </div>

      <div className="whatif-card">
        <span>AFTER CORRECTIVE ACTION</span>
        <strong>{whatIf.corrective_action?.risk}</strong>
        <small>
          Risk Score: {whatIf.corrective_action?.risk_score ?? "--"}/100
        </small>
        <small>
          Change:{" "}
          {whatIf.corrective_action?.change_from_current > 0
            ? "+"
            : ""}
          {whatIf.corrective_action?.change_from_current ?? "--"}
        </small>
      </div>

      <div className="whatif-card">
        <span>AFTER 7-DAY DELAY</span>
        <strong>{whatIf.seven_day_delay?.risk}</strong>
        <small>
          Risk Score: {whatIf.seven_day_delay?.risk_score ?? "--"}/100
        </small>
        <small>
          Change:{" "}
          {whatIf.seven_day_delay?.change_from_current > 0
            ? "+"
            : ""}
          {whatIf.seven_day_delay?.change_from_current ?? "--"}
        </small>
      </div>

    </div>

    <div className="whatif-recommendation">
      <span>AI RECOMMENDATION</span>
      <strong>{whatIf.recommendation}</strong>
    </div>

  </div>
)}


{explanationLoading && explanation?.mine_id === mine.mine_id && (
  <div className="ai-explanation-panel">
    ANALYZING MINE DATA...
  </div>
)}

{explanationError && explanation?.mine_id === mine.mine_id && (
  <div className="ai-explanation-panel explanation-error">
    {explanationError}
  </div>
)}

{explanation && explanation.mine_id === mine.mine_id && !explanationLoading && (
  <div className="ai-explanation-panel">
    <div className="explanation-title">
      AI GOVERNANCE ANALYSIS
    </div>

    <div className="explanation-risk">
      <span>RISK LEVEL</span>
      <strong>{explanation.risk_level}</strong>
    </div>

    <div className="explanation-drivers">
      <span>WHY THIS RISK?</span>

      {explanation.risk_drivers?.map((driver, index) => (
        <div key={index} className="explanation-driver">
          • {driver}
        </div>
      ))}
    </div>

    <div className="explanation-recommendation">
      <span>RECOMMENDED ACTION</span>
      <strong>{explanation.recommendation}</strong>
    </div>
  </div>
)}

                  </div>

                </div>

              ))}

            </div>
           
          )}

        </main>

      </div>
    );
  }
  /* =========================
   COMPLIANCE MONITORING PAGE
    ========================= */
if (page === "ai-assistant") {
  return (
    <div className="risk-page">

      <header className="risk-header">

        <div>
          <div className="risk-logo">
            S.I.G.M.A
          </div>

          <div className="risk-subtitle">
            SMART INTEGRATED GOVERNANCE FOR MINING ASSETS
          </div>
        </div>

        <div className="risk-header-actions">

          <button
            className="back-button"
            onClick={() => setPage("dashboard")}
          >
            ← COMMAND CENTER
          </button>

          <button
            className="logout-button"
            onClick={() => {
              setLoggedIn(false);
              setPage("dashboard");
            }}
          >
            LOGOUT
          </button>

        </div>

      </header>


      <main className="risk-content">

        <div className="ai-assistant-page">

          <div className="ai-assistant-title">
            🤖 SIGMA AI GOVERNANCE ASSISTANT
          </div>

          <p className="ai-assistant-description">
            AI-powered governance intelligence for mining operations
          </p>


          <div className="ai-assistant-card">

            <label className="ai-label">
              SELECT MINE
            </label>

            <select
              className="ai-mine-select"
              value={aiMine}
              onChange={(e) => setAiMine(e.target.value)}
            >
              <option value="M001">M001 — Demo Mine Alpha</option>
              <option value="M002">M002 — Demo Mine Beta</option>
            </select>


            <label className="ai-label">
              ASK SIGMA
            </label>

            <textarea
              className="ai-question-input"
              placeholder="Example: Why is M001 at risk?"
              value={aiQuestion}
              onChange={(e) => {
                setAiQuestion(e.target.value);
                setAiError("");
              }}
            />


            <button
              className="ai-ask-button"
              onClick={askSIGMA}
              disabled={aiLoading}
            >
              {aiLoading ? "ANALYZING..." : "ASK SIGMA →"}
            </button>


            {aiError && (
              <div className="ai-error">
                {aiError}
              </div>
            )}


          <div className="sigma-ai-messages">

  {aiMessages.length === 0 && (
    <div className="sigma-ai-welcome">
      <div className="sigma-ai-welcome-icon">🤖</div>

      <h3>Hi! I'm SIGMA.</h3>

      <p>
        Your AI governance assistant for mining operations.
        Ask me about risk, compliance, equipment,
        contractors or environmental conditions.
      </p>
    </div>
  )}

  {aiMessages.map((message, index) => (

    <div
      key={`${message.timestamp}-${index}`}
      className={
        message.role === "user"
          ? "sigma-ai-message user"
          : "sigma-ai-message assistant"
      }
    >

      <div className="sigma-ai-message-label">

        {message.role === "user"
          ? "YOU"
          : "SIGMA"}

      </div>

      <div className="sigma-ai-message-content">
        {message.content}
      </div>

    </div>

  ))}

  {aiLoading && (
    <div className="sigma-ai-message assistant">

      <div className="sigma-ai-message-label">
        SIGMA
      </div>

      <div className="sigma-ai-typing">
        <span></span>
        <span></span>
        <span></span>
      </div>

    </div>
  )}

</div>

          </div>


          <div className="ai-suggestions">

            <div className="ai-suggestions-title">
              SUGGESTED QUESTIONS
            </div>

            <button
              onClick={() =>
                setAiQuestion("Why is M001 at risk?")
              }
            >
              Why is this mine at risk?
            </button>

            <button
              onClick={() =>
                setAiQuestion("What should management do immediately?")
              }
            >
              What should management do immediately?
            </button>

            <button
              onClick={() =>
                setAiQuestion("Which compliance issues need attention?")
              }
            >
              Which compliance issues need attention?
            </button>

          </div>

        </div>

      </main>

    </div>
  );
}
if (page === "compliance") {
  return (
    <div className="risk-page">

      <header className="risk-header">

        <div>
          <div className="risk-logo">
            S.I.G.M.A
          </div>

          <div className="risk-subtitle">
            SMART INTEGRATED GOVERNANCE FOR MINING ASSETS
          </div>
        </div>

        <div className="risk-header-actions">

          <button
            className="back-button"
            onClick={() => setPage("dashboard")}
          >
            ← COMMAND CENTER
          </button>

          <button
            className="logout-button"
            onClick={() => {
              setLoggedIn(false);
              setPage("dashboard");
            }}
          >
            LOGOUT
          </button>

        </div>

      </header>

      <main className="risk-content">

        <div className="risk-title-section">
          <span>GOVERNANCE MODULE 02</span>

          <h1>
            Compliance Monitoring
          </h1>

          <p>
            Monitor inspections, violations and corrective actions
            across mining operations.
          </p>
        </div>

        <div className="risk-grid">

          <div className="risk-card compliance-stat">
  <span>TOTAL VIOLATIONS</span>
  <strong>
    {complianceData?.summary?.total_violations ?? "--"}
  </strong>
</div>

<div className="risk-card compliance-stat">
  <span>OPEN VIOLATIONS</span>
  <strong>
    {complianceData?.summary?.open_violations ?? "--"}
  </strong>
</div>

<div className="risk-card compliance-stat">
  <span>OVERDUE ACTIONS</span>
  <strong>
    {complianceData?.summary?.overdue_actions ?? "--"}
  </strong>
</div>

<div className="risk-card compliance-stat">
  <span>COMPLETED ACTIONS</span>
  <strong>
    {complianceData?.summary?.completed_actions ?? "--"}
  </strong>
</div>

        </div>
        {/* VIOLATION INTELLIGENCE */}

        <section className="compliance-section">

          <div className="compliance-section-header">
            <span>GOVERNANCE ALERTS</span>
            <h2>Violation Intelligence</h2>
            <p>
              Active and historical regulatory violations detected across mining operations.
            </p>
          </div>

          <div className="compliance-table-wrapper">

            <table className="compliance-table">

              <thead>
                <tr>
                  <th>Mine</th>
                  <th>Category</th>
                  <th>Severity</th>
                  <th>Regulation</th>
                  <th>Deadline</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>

                {complianceData?.violations?.map((violation) => (
                  <tr key={violation.violation_id}>

                    <td>{violation.mine_id}</td>

                    <td>{violation.category}</td>

                    <td>
                      <span className="severity-badge">
                        {violation.severity}
                      </span>
                    </td>

                    <td>{violation.regulation}</td>

                    <td>{violation.deadline}</td>

                    <td>
                      <span className="status-badge">
                        {violation.status}
                      </span>
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>

        </section>


      </main>
              {/* CORRECTIVE ACTION TRACKING */}

        <section className="compliance-section">

          <div className="compliance-section-header">
            <span>ACTION MANAGEMENT</span>

            <h2>
              Corrective Action Tracking
            </h2>

            <p>
              Track assigned actions, responsibilities, priorities and completion status.
            </p>
          </div>

          <div className="compliance-table-wrapper">

            <table className="compliance-table">

              <thead>
                <tr>
                  <th>Action</th>
                  <th>Priority</th>
                  <th>Assigned To</th>
                  <th>Deadline</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>

                {complianceData?.corrective_actions?.map((action) => (
                  <tr key={action.action_id}>

                    <td>
                      {action.action}
                    </td>

                    <td>
                      <span className="severity-badge">
                        {action.priority}
                      </span>
                    </td>

                    <td>
                      {action.assigned_to}
                    </td>

                    <td>
                      {action.deadline}
                    </td>

                    <td>
                      <span className="status-badge">
                        {action.status}
                      </span>
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>

          </div>

        </section>

    </div>
  );
}
/* =========================
   OPERATIONAL INTELLIGENCE PAGE
========================= */

if (page === "operational") {
  return (
    <div className="risk-page">

      <header className="risk-header">

        <div>
          <div className="risk-logo">
            S.I.G.M.A
          </div>

          <div className="risk-subtitle">
            SMART INTEGRATED GOVERNANCE FOR MINING ASSETS
          </div>
        </div>

        <div className="risk-header-actions">

          <button
            className="back-button"
            onClick={() => setPage("dashboard")}
          >
            ← COMMAND CENTER
          </button>

          <button
            className="logout-button"
            onClick={() => {
              setLoggedIn(false);
              setPage("dashboard");
            }}
          >
            LOGOUT
          </button>

        </div>

      </header>

      <main className="risk-content">

        <div className="risk-title-section">
          <span>GOVERNANCE MODULE 03</span>

          <h1>Operational Intelligence</h1>

          <p>
            Monitor equipment, contractors and operational conditions
            across mining operations.
          </p>
        </div>

        {operationalLoading && (
          <div className="risk-loading">
            LOADING OPERATIONAL INTELLIGENCE...
          </div>
        )}

        {operationalError && (
          <div className="risk-error">
            {operationalError}
          </div>
        )}

        {operationalData && (
          <>
            <div className="compliance-summary-grid">

              <div className="compliance-stat-card">
                <span>TOTAL EQUIPMENT</span>
                <strong>
                  {operationalData.summary.total_equipment}
                </strong>
              </div>

              <div className="compliance-stat-card">
                <span>MAINTENANCE DELAYS</span>
                <strong>
                  {operationalData.summary.maintenance_delays}
                </strong>
              </div>

              <div className="compliance-stat-card">
                <span>EQUIPMENT FAILURES</span>
                <strong>
                  {operationalData.summary.equipment_failures}
                </strong>
              </div>

              <div className="compliance-stat-card">
                <span>CONTRACTOR VIOLATIONS</span>
                <strong>
                  {operationalData.summary.contractor_violations}
                </strong>
              </div>

            </div>

            <section className="compliance-section">

              <div className="section-label">
                EQUIPMENT INTELLIGENCE
              </div>

              <h2>Equipment Monitoring</h2>

              <p>
                Current equipment condition, maintenance delays and
                failure patterns.
              </p>

              <div className="compliance-table-wrapper">

                <table className="compliance-table">

                  <thead>
                    <tr>
                      <th>Mine</th>
                      <th>Equipment</th>
                      <th>Maintenance Delay</th>
                      <th>Failures</th>
                      <th>Condition</th>
                    </tr>
                  </thead>

                  <tbody>

                    {operationalData.equipment.map((item) => (
                      <tr key={item.equipment_id}>

                        <td>{item.mine_id}</td>

                        <td>{item.equipment_type}</td>

                        <td>
                          {item.maintenance_delay_days} days
                        </td>

                        <td>
                          {item.failure_count}
                        </td>

                        <td>
                          <span className="status-badge">
                            {item.equipment_condition}
                          </span>
                        </td>

                      </tr>
                    ))}

                  </tbody>

                </table>

              </div>

            </section>

            <section className="compliance-section">

              <div className="section-label">
                CONTRACTOR INTELLIGENCE
              </div>

              <h2>Contractor Monitoring</h2>

              <p>
                Track contractor compliance and overdue actions.
              </p>

              <div className="compliance-table-wrapper">

                <table className="compliance-table">

                  <thead>
                    <tr>
                      <th>Mine</th>
                      <th>Contractor</th>
                      <th>Workers</th>
                      <th>Violations</th>
                      <th>Compliance Score</th>
                    </tr>
                  </thead>

                  <tbody>

                    {operationalData.contractors.map((item) => (
                      <tr key={item.contractor_id}>

                        <td>{item.mine_id}</td>

                        <td>{item.contractor_name}</td>

                        <td>{item.workers}</td>

                        <td>{item.previous_violations}</td>

                        <td>
                          {item.compliance_score}%
                        </td>

                      </tr>
                    ))}

                  </tbody>

                </table>

              </div>

            </section>

          </>
        )}

      </main>

    </div>
  );
}

/* =========================
   SUSTAINABILITY INTELLIGENCE PAGE
========================= */

if (page === "sustainability") {
  return (
    <div className="risk-page">

      <header className="risk-header">

        <div>
          <div className="risk-logo">
            S.I.G.M.A
          </div>

          <div className="risk-subtitle">
            SMART INTEGRATED GOVERNANCE FOR MINING ASSETS
          </div>
        </div>

        <div className="risk-header-actions">

          <button
            className="back-button"
            onClick={() => setPage("dashboard")}
          >
            ← COMMAND CENTER
          </button>

          <button
            className="logout-button"
            onClick={() => {
              setLoggedIn(false);
              setPage("dashboard");
            }}
          >
            LOGOUT
          </button>

        </div>

      </header>

      <main className="risk-content">

        <div className="risk-section-label">
          ENVIRONMENTAL INTELLIGENCE
        </div>

        <h1>Sustainability Intelligence</h1>

        <p className="risk-description">
          Monitor environmental conditions and sustainability risks across mining operations.
        </p>

        {sustainabilityLoading && (
          <p>Loading sustainability data...</p>
        )}

        {sustainabilityError && (
          <p>{sustainabilityError}</p>
        )}

        {sustainabilityData && (
          <>
            <div className="risk-summary-grid">

              <div className="risk-summary-card">
                <span>Total Records</span>
                <strong>
                  {sustainabilityData.summary.total_records}
                </strong>
              </div>

              <div className="risk-summary-card">
                <span>Environmental Violations</span>
                <strong>
                  {sustainabilityData.summary.environmental_violations}
                </strong>
              </div>

              <div className="risk-summary-card">
                <span>Average Dust</span>
                <strong>
                  {sustainabilityData.summary.average_dust}
                </strong>
              </div>

              <div className="risk-summary-card">
                <span>Average Noise</span>
                <strong>
                  {sustainabilityData.summary.average_noise}
                </strong>
              </div>

            </div>

            <section className="risk-section">

              <div className="risk-section-label">
                ENVIRONMENTAL MONITORING
              </div>

              <h2>Environmental Conditions</h2>

              <p className="risk-description">
                Current environmental measurements and detected violations.
              </p>

              <div className="risk-table-wrapper">

                <table className="risk-table">

                  <thead>
                    <tr>
                      <th>Mine</th>
                      <th>Dust Level</th>
                      <th>Air Quality</th>
                      <th>Water pH</th>
                      <th>Noise Level</th>
                      <th>Status</th>
                    </tr>
                  </thead>

                  <tbody>

                    {sustainabilityData.environment.map((item) => (
                      <tr key={item.record_id}>

                        <td>{item.mine_id}</td>

                        <td>{item.dust_level}</td>

                        <td>{item.air_quality}</td>

                        <td>{item.water_ph}</td>

                        <td>{item.noise_level}</td>

                        <td>
                          <span className="status-badge">
                            {item.environmental_violation === "Yes"
                              ? "Violation"
                              : "Normal"}
                          </span>
                        </td>

                      </tr>
                    ))}

                  </tbody>

                </table>

              </div>
<section className="risk-section">

  <div className="risk-section-label">
    ENVIRONMENTAL RISK INTELLIGENCE
  </div>

  <h2>Environmental Risk Assessment</h2>

  <p className="risk-description">
    AI-assisted assessment of environmental conditions and detected sustainability risks.
  </p>

  <div className="risk-table-wrapper">

    <table className="risk-table">

      <thead>
        <tr>
          <th>Mine</th>
          <th>Environmental Risk</th>
          <th>Primary Driver</th>
          <th>Dust</th>
          <th>Air Quality</th>
          <th>Noise</th>
          <th>Recommendation</th>
        </tr>
      </thead>

      <tbody>

        {sustainabilityData.environment.map((item) => {

          let risk = "LOW";
          let driver = "Normal conditions";
          let recommendation = "Continue routine environmental monitoring.";

          if (item.environmental_violation === "Yes") {
            risk = "HIGH";
            driver = "Environmental violation";
            recommendation = "Immediate environmental inspection required.";
          } else if (
            Number(item.dust_level) >= 80 ||
            Number(item.noise_level) >= 85 ||
            Number(item.air_quality) <= 60
          ) {
            risk = "MEDIUM";
            driver = "Elevated environmental parameter";
            recommendation = "Increase monitoring and corrective controls.";
          }

          return (
            <tr key={`risk-${item.record_id}`}>

              <td>{item.mine_id}</td>

              <td>
                <span className={`risk-badge ${risk.toLowerCase()}`}>
                  {risk}
                </span>
              </td>

              <td>{driver}</td>

              <td>{item.dust_level}</td>

              <td>{item.air_quality}</td>

              <td>{item.noise_level}</td>

              <td>{recommendation}</td>

            </tr>
          );

        })}

      </tbody>

    </table>

  </div>

</section>
            </section>

          </>
        )}

      </main>

    </div>
  );
}
  /* =========================
     COMMAND CENTER
     ========================= */

  return (
    <div className="dashboard">

      <header className="dashboard-header">

        <div>

          <div className="dashboard-logo">
            S.I.G.M.A
          </div>

          <div className="dashboard-subtitle">
            SMART INTEGRATED GOVERNANCE FOR MINING ASSETS
          </div>

        </div>

        <button
          className="logout-button"
          onClick={() => setLoggedIn(false)}
        >
          LOGOUT
        </button>

      </header>

      <main className="dashboard-content">

        <div className="dashboard-welcome">

          <span>COMMAND CENTER</span>

          <h1>
            Mining Governance Intelligence
          </h1>

          <p>
            Predictive risk, compliance monitoring and intelligent
            governance for modern mining operations.
          </p>

        </div>

        <div className="dashboard-grid">

          {/* CARD 01 */}

          <div
            className="dashboard-card clickable-card"
            onClick={openRiskPage}
          >

            <div className="card-number">
              01
            </div>

            <h2>
              Predictive Risk Analytics
            </h2>

            <p>
              AI-powered prediction of mine governance and
              compliance risks.
            </p>

            <div className="card-status">
              AI ENGINE READY →
            </div>

          </div>


          {/* CARD 02 */}

          
<div className="dashboard-card" onClick={openCompliancePage}>

  <div className="card-number">
    02
  </div>

  <h2>
    Compliance Monitoring
  </h2>

  <p>
    Monitor inspections, violations and regulatory
    compliance.
  </p>

  <div className="card-status">
    MONITORING ACTIVE
  </div>

</div>



          {/* CARD 03 */}

          <div
  className="dashboard-card clickable-card"
  onClick={openOperationalPage}
>

            <div className="card-number">
              03
            </div>

            <h2>
              Operational Efficiency
            </h2>

            <p>
              Monitor equipment, contractors and operational
              conditions.
            </p>

            <div className="card-status">
              SYSTEM ONLINE
            </div>

          </div>


          {/* CARD 04 */}

          <div
  className="dashboard-card"
  onClick={openSustainabilityPage}
>

            <div className="card-number">
              04
            </div>

            <h2>
              Sustainability Intelligence
            </h2>

            <p>
              Track environmental conditions and sustainability
              risks.
            </p>

            <div className="card-status">
              ENVIRONMENT ACTIVE
            </div>

          </div>
          
{/* SIGMA FLOATING AI ASSISTANT */}

{aiOpen && (
  <div className="sigma-ai-chat">

    
    {showConversations && (
      <div className="sigma-ai-history">
        <button className="sigma-ai-new-chat" onClick={startNewSIGMAChat}>
          ＋ NEW CHAT
        </button>
        <div className="sigma-ai-history-title">PREVIOUS CONVERSATIONS</div>
        {aiConversations.length === 0 ? (
          <div className="sigma-ai-history-empty">No previous conversations yet.</div>
        ) : (
          aiConversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`sigma-ai-history-item ${
                currentConversationId === conversation.id ? "active" : ""
              }`}
              onClick={() => loadSIGMAConversation(conversation)}
            >
              <div className="sigma-ai-history-item-title">{conversation.title}</div>
              <div className="sigma-ai-history-item-date">
                {new Date(conversation.updatedAt).toLocaleString()}
              </div>
              <button
                className="sigma-ai-history-delete"
                onClick={(event) => deleteSIGMAConversation(conversation.id, event)}
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
    )}

<div className="sigma-ai-chat-header">
      <div>
        <div className="sigma-ai-chat-title">
          🤖 SIGMA AI
        </div>

        <div className="sigma-ai-chat-subtitle">
          AI GOVERNANCE ASSISTANT
        </div>
      </div>

      
       <div className="sigma-ai-header-actions">
  <button
  className="sigma-ai-history-toggle"
  onClick={() => setShowConversations(!showConversations)}
  title="Previous conversations"
>
  ☰
</button>
<button
  className="sigma-ai-fullscreen"
  onClick={() => setAiFullScreen(!aiFullScreen)}
>
  {aiFullScreen ? "▣" : "⛶"}
</button>
  <button
    className="sigma-ai-close"
    onClick={() => setAiOpen(false)}
  >
    ×
  </button>

</div>
    </div>

    <div className="sigma-ai-chat-body">

      {!aiAnswer && !aiLoading && (
        <div className="sigma-ai-welcome">

          <div className="sigma-ai-avatar">
            🤖
          </div>

          <h3>Hi! I'm SIGMA.</h3>

          <p>
            Your AI governance assistant for mining operations.
            Ask me about risk, compliance, equipment,
            contractors or environmental conditions.
          </p>

        </div>
      )}
    
{aiMessages.length > 0 && (
  <div className="sigma-ai-messages">

    {aiMessages.map((message, index) => (
      <div
        key={`${message.timestamp}-${index}`}
        className={`sigma-ai-message ${
          message.role === "user"
            ? "user"
            : "assistant"
        }`}
      >

        <div className="sigma-ai-message-label">
          {message.role === "user" ? "YOU" : "SIGMA"}
        </div>

        <div className="sigma-ai-message-content">
          {message.content}
        </div>

      </div>
    ))}

  </div>
)}

      <div className="sigma-ai-suggestions">

        <div className="sigma-ai-section-title">
          QUICK QUESTIONS
        </div>

        <button
          onClick={() => {
            setAiQuestion("Why is M001 at risk?");
            setAiMine("M001");
          }}
        >
          Why is M001 at risk?
        </button>

        <button
          onClick={() => {
            setAiQuestion(
              "What should management do immediately?"
            );
            setAiMine("M001");
          }}
        >
          What should management do?
        </button>

        <button
          onClick={() => {
            setAiQuestion(
              "Which compliance issues need attention?"
            );
            setAiMine("M001");
          }}
        >
          Any compliance issues?
        </button>

      </div>

      {aiLoading && (
        <div className="sigma-ai-loading">
          SIGMA IS ANALYZING MINE DATA...
        </div>
      )}

      {aiError && (
        <div className="sigma-ai-error">
          {aiError}
        </div>
      )}

      {aiAnswer && (
        <div className="sigma-ai-answer">

          <div className="sigma-ai-message-label">
            SIGMA
          </div>

          <div className="sigma-ai-message">
            {aiAnswer}
          </div>

        </div>
      )}

    </div>

    <div className="sigma-ai-input-area">

      <button className="sigma-ai-new-chat-bottom" onClick={startNewSIGMAChat}>
  ＋ New Chat
</button>
<select
        value={aiMine}
        onChange={(e) => setAiMine(e.target.value)}
        className="sigma-ai-mine"
      >
        <option value="M001">
          M001 — Demo Mine Alpha
        </option>

        <option value="M002">
          M002 — Demo Mine Beta
        </option>
      </select>

      <div className="sigma-ai-input-row">

        <input
          type="text"
          value={aiQuestion}
          onChange={(e) => setAiQuestion(e.target.value)}
          placeholder="Ask SIGMA anything..."
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              askSIGMA();
            }
          }}
        />

        <button
          onClick={askSIGMA}
          disabled={aiLoading}
          className="sigma-ai-send"
        >
          →
        </button>

      </div>

    </div>

  </div>
)}
{aiFullScreen && (
  <div className="sigma-ai-fullscreen-panel">

    
    {showConversations && (
      <div className="sigma-ai-history sigma-ai-history-fullscreen">
        <button className="sigma-ai-new-chat" onClick={startNewSIGMAChat}>
          ＋ NEW CHAT
        </button>
        <div className="sigma-ai-history-title">PREVIOUS CONVERSATIONS</div>
        {aiConversations.length === 0 ? (
          <div className="sigma-ai-history-empty">No previous conversations yet.</div>
        ) : (
          aiConversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`sigma-ai-history-item ${
                currentConversationId === conversation.id ? "active" : ""
              }`}
              onClick={() => loadSIGMAConversation(conversation)}
            >
              <div className="sigma-ai-history-item-title">{conversation.title}</div>
              <div className="sigma-ai-history-item-date">
                {new Date(conversation.updatedAt).toLocaleString()}
              </div>
              <button
                className="sigma-ai-history-delete"
                onClick={(event) => deleteSIGMAConversation(conversation.id, event)}
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
    )}

<div className="sigma-ai-fullscreen-header">
      <div>
        <div className="sigma-ai-fullscreen-title">
          🤖 SIGMA AI
        </div>
        <div className="sigma-ai-fullscreen-subtitle">
          AI GOVERNANCE ASSISTANT
        </div>
      </div>
       <button
         className="sigma-ai-history-toggle"
         onClick={() => setShowConversations(!showConversations)}
         title="Previous conversations"
       >
         ☰
       </button>


      <button
        className="sigma-ai-fullscreen-close"
        onClick={() => setAiFullScreen(false)}
      >
        ×
      </button>
    </div>

    <div className="sigma-ai-fullscreen-content">

      <div className="sigma-ai-fullscreen-welcome">
        <div className="sigma-ai-avatar">🤖</div>

        <h1>Hi! I'm SIGMA.</h1>

        <p>
          Your AI governance assistant for mining operations.
          Ask me about risk, compliance, equipment, contractors
          or environmental conditions.
        </p>
      </div>

     {aiMessages.length > 0 && (
  <div className="sigma-ai-fullscreen-messages">

    {aiMessages.map((message, index) => (
      <div
        key={`${message.timestamp}-${index}`}
        className={`sigma-ai-fullscreen-message ${
          message.role === "user" ? "user" : "assistant"
        }`}
      >

        <div className="sigma-ai-fullscreen-message-label">
          {message.role === "user" ? "YOU" : "SIGMA"}
        </div>

        <div className="sigma-ai-fullscreen-message-content">
          {message.content}
        </div>

      </div>
    ))}

  </div>
)}

    </div>

    <div className="sigma-ai-fullscreen-input">
      <button
  className="sigma-ai-new-chat-fullscreen"
  onClick={startNewSIGMAChat}
>
  ＋ New Chat
</button>
<input
        value={aiQuestion}
        onChange={(e) => setAiQuestion(e.target.value)}
        placeholder="Ask SIGMA anything..."
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            askSIGMA();
          }
        }}
      />

      <button onClick={askSIGMA}>
        →
      </button>
    </div>

  </div>
)}

<button
  className="sigma-ai-floating-button"
  onClick={() => setAiOpen(!aiOpen)}
>
  🤖
  <span>SIGMA AI</span>
</button>
</div>
      </main>

    </div>
  );
}

export default App;

