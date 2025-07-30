from runagent import RunAgentClient

ra = RunAgentClient(
    agent_id="30ff8384-6183-44bc-acd0-34b363adf465",
    local=True
    )


agent_results = ra.run_generic(
    sender_name="Alice Johnson",
    recipient_name="Mr. Daniel Smith",
    subject="Request for Meeting Next Week"
)

print(agent_results)