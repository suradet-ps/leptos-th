# การส่ง children ให้คอมโพเนนต์

เป็นเรื่องปกติมากที่คุณจะอยากส่งลูก (children) เข้าไปในคอมโพเนนต์ เช่นเดียวกับที่คุณ
ส่ง children เข้าไปในเอลิเมนต์ HTML ได้ ตัวอย่างเช่น สมมติว่าเรามีคอมโพเนนต์ `<FancyForm/>`
ที่ช่วยเสริมความสามารถให้กับ `<form>` ของ HTML เราจำเป็นต้องมีวิธีส่งอินพุตทั้งหมดของมันเข้าไป

```rust
view! {
    <FancyForm>
        <fieldset>
            <label>
                "Some Input"
                <input type="text" name="something"/>
            </label>
        </fieldset>
        <button>"Submit"</button>
    </FancyForm>
}
```

ทำแบบนี้ใน Leptos ได้อย่างไร? โดยพื้นฐานแล้วมีสองวิธีในการส่งคอมโพเนนต์
ไปยังคอมโพเนนต์อื่น:

1. **render props**: พร็อพที่เป็นฟังก์ชันซึ่งคืนค่าออกมาเป็นวิว
2. พร็อพ **`children`**: พร็อพพิเศษของคอมโพเนนต์ที่รวมทุกอย่าง
   ที่คุณส่งเป็น children ให้กับคอมโพเนนต์

อันที่จริง คุณได้เห็นทั้งสองแบบนี้ใช้งานจริงมาแล้วในคอมโพเนนต์ [`<Show/>`](/view/06_control_flow.html#show):

```rust
view! {
  <Show
    // `when` is a normal prop
    when=move || value.get() > 5
    // `fallback` is a "render prop": a function that returns a view
    fallback=|| view! { <Small/> }
  >
    // `<Big/>` (and anything else here)
    // will be given to the `children` prop
    <Big/>
  </Show>
}
```

มาเขียนคอมโพเนนต์ที่รับ children และ render prop กัน

```rust
/// Displays a `render_prop` and some children within markup.
#[component]
pub fn TakesChildren<F, IV>(
    /// Takes a function (type F) that returns anything that can be
    /// converted into a View (type IV)
    render_prop: F,
    /// `children` can take one of several different types, each of which
    /// is a function that returns some view type
    children: Children,
) -> impl IntoView
where
    F: Fn() -> IV,
    IV: IntoView,
{
    view! {
        <h1><code>"<TakesChildren/>"</code></h1>
        <h2>"Render Prop"</h2>
        {render_prop()}
        <hr/>
        <h2>"Children"</h2>
        {children()}
    }
}
```

`render_prop` และ `children` ต่างก็เป็นฟังก์ชัน เราจึงเรียกพวกมันเพื่อสร้าง
วิวที่เหมาะสมได้ โดยเฉพาะ `Children` ซึ่งเป็นนามแฝงของ
`Box<dyn FnOnce() -> AnyView>` (ดีใจไหมล่ะที่เราตั้งชื่อมันว่า `Children` แทน?)
`AnyView` ที่คืนค่ามาเป็นวิวแบบทึบที่ลบข้อมูลชนิดออกแล้ว: คุณไม่สามารถทำอะไร
เพื่อตรวจสอบดูภายในมันได้ ยังมีชนิดของลูกอื่นๆ อีกหลากหลาย ตัวอย่างเช่น `ChildrenFragment`
จะคืนค่าเป็น `Fragment` ซึ่งเป็นคอลเลกชันที่สามารถวนซ้ำ children ภายในได้

> ถ้าคุณต้องการ `Fn` หรือ `FnMut` ตรงนี้เพราะต้องเรียก `children` มากกว่าหนึ่งครั้ง
> เราก็มีนามแฝง `ChildrenFn` และ `ChildrenMut` ให้ใช้ด้วย

เราใช้คอมโพเนนต์นี้ได้แบบนี้:

```rust
view! {
    <TakesChildren render_prop=|| view! { <p>"Hi, there!"</p> }>
        // these get passed to `children`
        "Some text"
        <span>"A span"</span>
    </TakesChildren>
}
```

## children ที่มีชนิด: สล็อต

จนถึงตอนนี้ เราได้พูดคุยกันถึงคอมโพเนนต์ที่มีพร็อพ `children` เดียว แต่บางครั้งการสร้างคอมโพเนนต์ที่มี children หลายตัวที่ต่างชนิดกันก็มีประโยชน์ ตัวอย่างเช่น:
```rust
view! {
    <If condition=a_is_true>
        <Then>"Show content when a is true"</Then>
        <ElseIf condition=b_is_true>"b is true"</ElseIf>
        <ElseIf condition=c_is_true>"c is true"</ElseIf>
        <Else>"None of the above are true"</Else>
    </If>
}
```
คอมโพเนนต์ `If` คาดหวัง child ที่เป็น `Then` เสมอ โดยอาจมี `ElseIf` หลายตัวหรือไม่มีเลย และมี `Else` แบบไม่บังคับก็ได้ เพื่อรองรับเรื่องนี้ Leptos จึงมี[สล็อต (slot)](https://docs.rs/leptos/latest/leptos/attr.slot.html) ให้

มาโคร `#[slot]` ใช้กำกับสตรัคต์ Rust ธรรมดาให้เป็นสล็อตของคอมโพเนนต์:
```rust
// A simple struct annotated with `#[slot]`,
// which expects children
#[slot]
struct Then {
    children: ChildrenFn,
}
```

สล็อตนี้ใช้เป็นพร็อพในคอมโพเนนต์ได้:
```rust
#[component]
fn If(
    condition: Signal<bool>,
    // Component slot, should be passed through the <Then slot> syntax
    then_slot: Then,
) -> impl IntoView {
    move || {
        if condition.get() {
            (then_slot.children)().into_any()
        } else {
            ().into_any()
        }
    }
}
```

ตอนนี้คอมโพเนนต์ `If` คาดหวัง child ที่มีชนิดเป็น `Then` คุณจะต้องระบุสล็อตที่ใช้ด้วย `slot:<prop_name>`:
```rust
view! {
    <If condition=a_is_true>
        // The `If` component always expects a `Then` child for `then_slot`
        <Then slot:then_slot>"Show content when a is true"</Then>
    </If>
}
```

> การระบุ `slot` โดยไม่ใส่ชื่อจะทำให้สล็อตที่เลือกมีค่าเริ่มต้นเป็นชื่อของสตรัคต์ในรูปแบบ snake case ดังนั้นในกรณีนี้ `<Then slot>` จะเทียบเท่ากับ `<Then slot:then>`

ดูตัวอย่างฉบับสมบูรณ์ได้ที่ [ตัวอย่างสล็อต](https://github.com/leptos-rs/leptos/tree/main/examples/slots)

### ตัวจัดการเหตุการณ์บนสล็อต

ตัวจัดการเหตุการณ์ไม่สามารถระบุลงบนสล็อตโดยตรงแบบนี้ได้:
```rust
<ComponentWithSlot>
    // ⚠️ Event handler `on:click` directly on slot is not allowed
    <SlotWithChildren slot:slot on:click=move |_| {}> 
        <h1>"Hello, World!"</h1>
    </SlotWithChildren>
</ComponentWithSlot>
```

ให้ห่อเนื้อหาของสล็อตไว้ในเอลิเมนต์ปกติแล้วติดตัวจัดการเหตุการณ์ไว้ตรงนั้นแทน:
```rust
<ComponentWithSlot>
    <SlotWithChildren slot:slot>
        // ✅ Event handler is not defined directly on slot
        <div on:click=move |_| {}>
            <h1>"Hello, World!"</h1>
        </div>
    </SlotWithChildren>
</ComponentWithSlot>
```

## การจัดการ children

ชนิด [`Fragment`](https://docs.rs/leptos/latest/leptos/tachys/view/fragment/struct.Fragment.html) โดยพื้นฐานแล้วเป็น
วิธีห่อ `Vec<AnyView>` คุณแทรกมันเข้าไปที่ไหนก็ได้ในวิวของคุณ

แต่คุณยังเข้าถึงวิวภายในเหล่านั้นโดยตรงเพื่อจัดการกับมันได้ด้วย ตัวอย่างเช่น นี่คือ
คอมโพเนนต์ที่รับ children ของมันแล้วเปลี่ยนให้เป็นรายการแบบไม่มีลำดับ

```rust
/// Wraps each child in an `<li>` and embeds them in a `<ul>`.
#[component]
pub fn WrapsChildren(children: ChildrenFragment) -> impl IntoView {
    // children() returns a `Fragment`, which has a
    // `nodes` field that contains a Vec<View>
    // this means we can iterate over the children
    // to create something new!
    let children = children()
        .nodes
        .into_iter()
        .map(|child| view! { <li>{child}</li> })
        .collect::<Vec<_>>();

    view! {
        <h1><code>"<WrapsChildren/>"</code></h1>
        // wrap our wrapped children in a UL
        <ul>{children}</ul>
    }
}
```

การเรียกใช้แบบนี้จะสร้างรายการขึ้นมา:

```rust
view! {
    <WrapsChildren>
        "A"
        "B"
        "C"
    </WrapsChildren>
}
```

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox.](https://codesandbox.io/p/devbox/9-component-children-0-7-736s9r?file=%2Fsrc%2Fmain.rs%3A1%2C1-90%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/9-component-children-0-7-736s9r?file=%2Fsrc%2Fmain.rs%3A1%2C1-90%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;

// Often, you want to pass some kind of child view to another
// component. There are two basic patterns for doing this:
// - "render props": creating a component prop that takes a function
//   that creates a view
// - the `children` prop: a special property that contains content
//   passed as the children of a component in your view, not as a
//   property

#[component]
pub fn App() -> impl IntoView {
    let (items, set_items) = signal(vec![0, 1, 2]);
    let render_prop = move || {
        let len = move || items.read().len();
        view! {
            <p>"Length: " {len}</p>
        }
    };

    view! {
        // This component just displays the two kinds of children,
        // embedding them in some other markup
        <TakesChildren
            // for component props, you can shorthand
            // `render_prop=render_prop` => `render_prop`
            // (this doesn't work for HTML element attributes)
            render_prop
        >
            // these look just like the children of an HTML element
            <p>"Here's a child."</p>
            <p>"Here's another child."</p>
        </TakesChildren>
        <hr/>
        // This component actually iterates over and wraps the children
        <WrapsChildren>
            <p>"Here's a child."</p>
            <p>"Here's another child."</p>
        </WrapsChildren>
    }
}

/// Displays a `render_prop` and some children within markup.
#[component]
pub fn TakesChildren<F, IV>(
    /// Takes a function (type F) that returns anything that can be
    /// converted into a View (type IV)
    render_prop: F,
    /// `children` takes the `Children` type
    /// this is an alias for `Box<dyn FnOnce() -> Fragment>`
    /// ... aren't you glad we named it `Children` instead?
    children: Children,
) -> impl IntoView
where
    F: Fn() -> IV,
    IV: IntoView,
{
    view! {
        <h1><code>"<TakesChildren/>"</code></h1>
        <h2>"Render Prop"</h2>
        {render_prop()}
        <hr/>
        <h2>"Children"</h2>
        {children()}
    }
}

/// Wraps each child in an `<li>` and embeds them in a `<ul>`.
#[component]
pub fn WrapsChildren(children: ChildrenFragment) -> impl IntoView {
    // children() returns a `Fragment`, which has a
    // `nodes` field that contains a Vec<View>
    // this means we can iterate over the children
    // to create something new!
    let children = children()
        .nodes
        .into_iter()
        .map(|child| view! { <li>{child}</li> })
        .collect::<Vec<_>>();

    view! {
        <h1><code>"<WrapsChildren/>"</code></h1>
        // wrap our wrapped children in a UL
        <ul>{children}</ul>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
