#!/usr/bin/env python3
"""
Quick test of the BidirectionalLinkEngine implementation.
Tests the core functionality with the existing knowledge base.
"""

import sys
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from backend.core.bidirectional_links import BidirectionalLinkEngine
from backend.knowledge.note_manager import NoteManager


def main():
    """Test the bidirectional links engine."""
    print("🔮 Testing ArcanAgent Bidirectional Links Engine")
    print("=" * 50)
    
    # Initialize the engine
    knowledge_base_path = "./knowledge_base"
    print(f"📁 Initializing with knowledge base: {knowledge_base_path}")
    
    try:
        # Create link engine
        link_engine = BidirectionalLinkEngine(knowledge_base_path)
        print("✅ BidirectionalLinkEngine created")
        
        # Refresh knowledge base
        link_engine.refresh_knowledge_base()
        print("✅ Knowledge base refreshed")
        
        # Get statistics
        stats = link_engine.get_graph_statistics()
        print(f"\n📊 Graph Statistics:")
        print(f"   Total notes: {stats['total_notes']}")
        print(f"   Total links: {stats['total_links']}")
        print(f"   Average links per note: {stats['avg_links_per_note']:.2f}")
        print(f"   Graph density: {stats['graph_density']:.4f}")
        print(f"   Most connected note: {stats['most_connected_note']}")
        print(f"   Orphaned notes: {stats['orphaned_notes']}")
        
        # Test note analysis if we have notes
        if stats['total_notes'] > 0:
            # Find a note to analyze
            first_note = next(iter(link_engine.note_metadata.keys()))
            print(f"\n🔍 Analyzing note: {first_note}")
            
            analysis = link_engine.analyze_note(first_note)
            if analysis:
                print(f"   Outgoing links: {len(analysis.outgoing_links)}")
                print(f"   Incoming links: {len(analysis.incoming_links)}")
                print(f"   Link density: {analysis.link_density:.4f}")
                print(f"   Granularity score: {analysis.granularity_score:.4f}")
                print(f"   Context layers: {list(analysis.context_layers.keys())}")
                
                # Show some links if they exist
                if analysis.outgoing_links:
                    print(f"   Sample outgoing links: {list(analysis.outgoing_links)[:3]}")
                if analysis.incoming_links:
                    print(f"   Sample incoming links: {list(analysis.incoming_links)[:3]}")
        
        # Test note manager integration
        print(f"\n📝 Testing NoteManager integration...")
        note_manager = NoteManager(knowledge_base_path, link_engine)
        
        # List notes
        notes_result = note_manager.list_notes(limit=5)
        print(f"   Found {notes_result['total']} notes total")
        print(f"   Showing first {len(notes_result['notes'])} notes:")
        
        for note in notes_result['notes'][:3]:
            print(f"   - {note['title']} (ID: {note['id']}, Links: {note['link_count']})")
        
        print(f"\n✅ All tests completed successfully!")
        print(f"🔗 Bidirectional Linking is All You Need! ✨")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())