def build_source_context(daily, claap, fathom, jira):
    return f"""
        #### Daily Status Updates:
        <<START OF DAILY STATUS UPDATES>>
        {daily}
        <<END OF DAILY STATUS UPDATES>>

        ---

        #### Claap Transcripts:
        <<START OF CLAAP TRANSCRIPTS>>
        {claap}
        <<END OF CLAAP TRANSCRIPTS>>

        ---

        #### Fathom Transcripts:
        <<START OF FATHOM TRANSCRIPTS>>
        {fathom}
        <<END OF FATHOM TRANSCRIPTS>>

        ---

        #### JIRA Tickets:
        <<START OF JIRA TICKETS>>
        {jira}
        <<END OF JIRA TICKETS>>
    """
