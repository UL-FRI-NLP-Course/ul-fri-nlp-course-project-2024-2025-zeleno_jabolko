from bert_score import score

def test_bertscore_sanity():
    """Test BERTScore with obviously different texts to check if it's working correctly."""
    
    print("Testing BERTScore with obviously different texts...")
    
    # Test 1: Identical texts (should score very high)
    identical_ref = "The weather is sunny today."
    identical_pred = "The weather is sunny today."
    
    # Test 2: Similar meaning (should score high)
    similar_ref = "The weather is sunny today."
    similar_pred = "Today the sun is shining brightly."
    
    # Test 3: Completely different content (should score low)
    different_ref = "The weather is sunny today."
    different_pred = "The economy is experiencing rapid growth due to technological innovations."
    
    # Test 4: Random text (should score very low)
    random_ref = "The weather is sunny today."
    random_pred = "Banana helicopter purple mathematics seventeen."
    
    test_cases = [
        (identical_ref, identical_pred, "Identical"),
        (similar_ref, similar_pred, "Similar meaning"),
        (different_ref, different_pred, "Different content"),
        (random_ref, random_pred, "Random text")
    ]
    
    references = [case[0] for case in test_cases]
    predictions = [case[1] for case in test_cases]
    labels = [case[2] for case in test_cases]
    
    # Calculate BERTScore
    P, R, F1 = score(predictions, references, lang="en", verbose=True, model_type="bert-base-uncased")
    
    print(f"\nBERTScore Test Results:")
    print("=" * 60)
    print(f"{'Test Case':<20} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 60)
    
    for i, label in enumerate(labels):
        p_score = P[i].item()
        r_score = R[i].item()
        f1_score = F1[i].item()
        print(f"{label:<20} {p_score:<12.4f} {r_score:<12.4f} {f1_score:<12.4f}")
    
    # Check if scores make sense
    f1_scores = [F1[i].item() for i in range(len(test_cases))]
    
    if f1_scores[0] > 0.95:  # Identical
        print(f"\n✓ Identical text test passed")
    else:
        print(f"\n✗ Identical text test failed: {f1_scores[0]:.4f}")
    
    if f1_scores[3] < 0.5:  # Random
        print(f"✓ Random text test passed")
    else:
        print(f"✗ Random text test failed: {f1_scores[3]:.4f}")
        
    if f1_scores[0] > f1_scores[1] > f1_scores[2] > f1_scores[3]:
        print(f"✓ Score ordering is correct")
    else:
        print(f"✗ Score ordering is incorrect")
        print(f"  Scores: {f1_scores}")

if __name__ == "__main__":
    test_bertscore_sanity() 