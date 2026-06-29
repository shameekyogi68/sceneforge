import os
import sys
import uuid
import time
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

# Add the workspace root to Python path
sys.path.append("/Users/shameekyogi/My Apps/ScriptForge")

# Load environment variables
dotenv_path = "/Users/shameekyogi/My Apps/ScriptForge/.env"
load_dotenv(dotenv_path)

import fitz  # PyMuPDF
from supabase import create_client
import backend.config as config
from backend.auth import login as auth_login, signup as auth_signup, get_current_user
from backend.rag import answer_with_sources, process_and_store_pdf

# Initialize Supabase Admin client to verify and clean up
supabase = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)

def generate_test_pdf(filename: str, content: str) -> str:
    """Create a simple test PDF with some text."""
    doc = fitz.open()
    page = doc.new_page()
    rect = fitz.Rect(50, 50, 550, 800)
    page.insert_textbox(rect, content, fontsize=12, fontname="helv")
    pdf_path = f"uploads/{filename}"
    doc.save(pdf_path)
    doc.close()
    return pdf_path

def main():
    print("=== STARTING SCENEFORGE E2E VERIFICATION ===")
    
    # Generate unique credentials
    test_id = str(uuid.uuid4())[:8]
    test_email = f"verify_sceneforge_{test_id}@gmail.com"
    test_password = "Password123!"
    project_name = f"VerifyProject_{test_id}"
    pdf_filename = f"verify_script_{test_id}.pdf"
    
    pdf_content = (
        "SCENEFORGE VERIFICATION SCRIPT\n\n"
        "This is a test document created to verify the end-to-end RAG pipeline of SceneForge.\n"
        "The secret keyword for verification is: BLUE_MONKEY_42.\n"
        "Filming location: the high cliffs of Bandra, Bombay.\n"
        "Lead character: Kabir, an ambitious scriptwriter."
    )
    
    print(f"Generated test email: {test_email}")
    print(f"Generated test project: {project_name}")
    print(f"Generated test PDF: {pdf_filename}")
    
    # Ensure uploads folder exists
    Path("uploads").mkdir(exist_ok=True)
    temp_pdf_path = None
    user_id = None
    project_id = None
    document_id = None
    
    try:
        # 1. Sign Up Test
        print("\nStep 1: Signing up new user...")
        signup_res = auth_signup(test_email, test_password)
        user_id = str(signup_res.user.id)
        print(f"Signup successful. User ID: {user_id}")
        
        # 2. Login Test
        print("\nStep 2: Logging in user...")
        login_res = auth_login(test_email, test_password)
        token = login_res.session.access_token
        print("Login successful. Acquired access token.")
        
        # 3. Project Creation
        print("\nStep 3: Creating a project...")
        project_id = str(uuid.uuid4())
        supabase.postgrest.auth(token)
        proj_insert = supabase.table("projects").insert({
            "id": project_id,
            "name": project_name,
            "user_id": user_id
        }).execute()
        print(f"Project created successfully. Project ID: {project_id}")
        
        # 4. Generate & Process PDF
        print("\nStep 4: Generating and processing test PDF...")
        temp_pdf_path = generate_test_pdf(pdf_filename, pdf_content)
        
        doc_insert = supabase.table("documents").insert({
            "project_id": project_id,
            "filename": pdf_filename,
            "status": "processing"
        }).execute()
        res_data = doc_insert.data
        if not isinstance(res_data, list) or not res_data:
            raise RuntimeError("Failed to insert document.")
        first_row = res_data[0]
        if not isinstance(first_row, dict):
            raise RuntimeError("Failed to insert document.")
        document_id = str(first_row.get("id"))
        
        # Process and store chunk vectors
        print("Parsing PDF and generating embeddings...")
        chunks_count = process_and_store_pdf(
            temp_pdf_path,
            pdf_filename,
            project_id,
            document_id=document_id,
            token=token
        )
        print(f"Processed successfully! Created {chunks_count} vector chunks.")
        
        # Update status to ready
        supabase.table("documents").update({"status": "ready"}).eq("id", document_id).execute()
        print("Document status updated to 'ready' in Supabase.")
        
        # 5. RAG Answer & Source Citations
        print("\nStep 5: Testing RAG search & Gemini answer...")
        question = "What is the secret keyword and who is the lead character?"
        print(f"Asking: '{question}'")
        
        answer, sources = answer_with_sources(question, project_id, project_memory="", token=token)
        
        print("\n--- GEMINI ANSWER ---")
        print(answer)
        print("---------------------")
        print("\n--- SOURCES CITED ---")
        for idx, src in enumerate(sources):
            print(f"Source {idx+1}: {src['filename']} (page {src['page']})")
            print(f"Preview: {src['text_preview']}")
        print("---------------------")
        
        # Validation checks
        assert "BLUE_MONKEY_42" in answer, "Verification keyword not found in the answer!"
        assert "Kabir" in answer, "Lead character name not found in the answer!"
        assert len(sources) > 0, "No sources were cited!"
        print("\nVerification checks: PASSED!")
        
    except Exception as e:
        print(f"\nVerification FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        print("\nStep 6: Cleaning up test data...")
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
            print("Removed local temp PDF.")
            
        if project_id:
            try:
                # CASCADE deletion will clean up messages, documents, chunks in Supabase
                supabase.table("projects").delete().eq("id", project_id).execute()
                print("Deleted test project (Cascaded documents and chunks deleted).")
            except Exception as e:
                print(f"Failed to delete test project: {e}")
                
        if user_id:
            try:
                # Delete user using auth admin API
                # NOTE: anon client cannot delete users, but we can do it via sql or leave it.
                # Let's try auth admin api
                supabase.auth.admin.delete_user(user_id)
                print("Deleted test user.")
            except Exception as e:
                # If admin is not permitted, we can delete the profile row at least
                try:
                    supabase.table("profiles").delete().eq("id", user_id).execute()
                    print("Deleted test profile row.")
                except Exception:
                    pass
                
        print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    main()
