"""
Demo applications for EasyGUI
"""

from .core import App, Color, app, text, button, space, close

def demo_basic():
    """Basic demo showing the simple API."""
    app = App("EasyGUI Demo - Basic", 500, 300)
    
    app.text("Welcome to EasyGUI!", Color.BLUE)
    app.text("The easiest way to make Windows GUIs!")
    app.space(10)
    
    app.button("Say Hello", lambda: print("Hello from EasyGUI!"))
    app.button("Change Title", lambda: setattr(app, 'title', 'Title Changed!'))
    app.button("Close App", app.close)
    
    app.run()

def demo_decorator():
    """Demo using the decorator style."""
    @app("EasyGUI Demo - Decorator Style", 400, 250)
    def my_app():
        text("This app was created with a decorator!", Color.GREEN)
        space(20)
        button("Print Message", lambda: print("Decorator style is cool!"))
        button("Exit", close)

def demo_counter():
    """Demo showing a simple counter app."""
    counter = {'value': 0}
    
    app = App("Counter App", 300, 200)
    
    def update_display():
        app.widgets.clear()
        app._current_y = 20
        app.text(f"Counter: {counter['value']}", Color.BLUE)
        app.space(10)
        app.button("+1", lambda: [counter.update({'value': counter['value'] + 1}), update_display()])
        app.button("-1", lambda: [counter.update({'value': counter['value'] - 1}), update_display()])
        app.button("Reset", lambda: [counter.update({'value': 0}), update_display()])
        app.refresh()
    
    update_display()
    app.run()

def main():
    """Main entry point for the demo command."""
    print("EasyGUI Demo Launcher")
    print("Choose a demo:")
    print("1. Basic API demo")
    print("2. Decorator style demo") 
    print("3. Counter app demo")
    
    choice = input("Enter choice (1-3): ").strip()
    
    try:
        if choice == "1":
            demo_basic()
        elif choice == "2":
            demo_decorator()
        elif choice == "3":
            demo_counter()
        else:
            print("Invalid choice, running basic demo...")
            demo_basic()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("Demo finished!")

if __name__ == "__main__":
    main()