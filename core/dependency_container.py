from typing import Dict, Type, Any, Optional, Callable
from threading import Lock


class DependencyContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._lock = Lock()
    
    def register_singleton(self, service_name: str, instance: Any) -> None:
        """Register a singleton instance"""
        with self._lock:
            self._singletons[service_name] = instance
    
    def register_factory(self, service_name: str, factory: Callable) -> None:
        """Register a factory function for creating instances"""
        with self._lock:
            self._factories[service_name] = factory
    
    def register_transient(self, service_name: str, service_type: Type, *args, **kwargs) -> None:
        """Register a transient service (new instance each time)"""
        def factory():
            return service_type(*args, **kwargs)
        self.register_factory(service_name, factory)
    
    def get(self, service_name: str) -> Any:
        """Get a service instance"""
        with self._lock:
            # Check singletons first
            if service_name in self._singletons:
                return self._singletons[service_name]
            
            # Check factories
            if service_name in self._factories:
                return self._factories[service_name]()
            
            raise ValueError(f"Service '{service_name}' not registered")
    
    def get_or_none(self, service_name: str) -> Optional[Any]:
        """Get a service instance or None if not found"""
        try:
            return self.get(service_name)
        except ValueError:
            return None
    
    def clear(self) -> None:
        """Clear all registered services"""
        with self._lock:
            self._services.clear()
            self._factories.clear()
            self._singletons.clear()


# Global container instance
container = DependencyContainer()


def get_container() -> DependencyContainer:
    """Get the global dependency container"""
    return container


def reset_container() -> None:
    """Reset the global container (useful for testing)"""
    global container
    container = DependencyContainer()