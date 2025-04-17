CREATE TABLE resume_summary2 AS
SELECT
  file_name,
  
  -- Extract Role
  TRIM(SUBSTR(
    resume_text,
    INSTR(resume_text, 'Role -') + LENGTH('Role -'),
    INSTR(resume_text, 'Gmail ID -') - INSTR(resume_text, 'Role -') - LENGTH('Role -')
  )) AS role,
  
  -- Extract Gmail ID
  TRIM(SUBSTR(
    resume_text,
    INSTR(resume_text, 'Gmail ID -') + LENGTH('Gmail ID -'),
    INSTR(resume_text, 'Work Experience -') - INSTR(resume_text, 'Gmail ID -') - LENGTH('Gmail ID -')
  )) AS gmail,
  
  -- Extract Work Experience
  TRIM(SUBSTR(
    resume_text,
    INSTR(resume_text, 'Work Experience -') + LENGTH('Work Experience -'),
    INSTR(resume_text, 'Skills -') - INSTR(resume_text, 'Work Experience -') - LENGTH('Work Experience -')
  )) AS experience,
  
  -- Extract Skills (till end of text)
  TRIM(SUBSTR(
    resume_text,
    INSTR(resume_text, 'Skills -') + LENGTH('Skills -')
  )) AS skills

FROM resume;
