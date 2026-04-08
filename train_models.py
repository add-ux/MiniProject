# train_real_models.py - Simple launcher for training
from real_dataset_trainer import RealDatasetTrainer

def main():
    print("\n" + "="*60)
    print("🎯 Starting ML Model Training")
    print("="*60)
    
    trainer = RealDatasetTrainer()
    results = trainer.run_complete_training()
    
    print("\n" + "="*60)
    print("✅ Models are ready!")
    print("="*60)
    print("\n📁 Model files saved in 'models/'")
    print("🚀 Now run: python app.py")
    print("="*60)

if __name__ == "__main__":
    main()